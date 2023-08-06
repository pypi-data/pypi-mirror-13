#-#  Copyright 2013-2016 Karlsruhe Institute of Technology
#-#
#-#  Licensed under the Apache License, Version 2.0 (the "License");
#-#  you may not use this file except in compliance with the License.
#-#  You may obtain a copy of the License at
#-#
#-#      http://www.apache.org/licenses/LICENSE-2.0
#-#
#-#  Unless required by applicable law or agreed to in writing, software
#-#  distributed under the License is distributed on an "AS IS" BASIS,
#-#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#-#  See the License for the specific language governing permissions and
#-#  limitations under the License.

import os, gzip
from grid_control import utils
from grid_control.config import ConfigError
from grid_control.datasets.splitter_base import DataSplitter, DataSplitterIO
from grid_control.utils.file_objects import VirtualFile
from grid_control.utils.parsing import parseList
from grid_control.utils.thread_tools import GCLock
from python_compat import BytesBuffer, bytes2str, ifilter, imap, lfilter, lmap, tarfile

class BaseJobFileTarAdaptor(object):
	def __init__(self, path):
		log = utils.ActivityLog('Reading job mapping file')
		self._mutex = GCLock()
		self._fmt = utils.DictFormat()
		self._tar = tarfile.open(path, 'r:')
		(self._cacheKey, self._cacheTar) = (None, None)

		metadata = self._fmt.parse(self._tar.extractfile('Metadata').readlines(), keyParser = {None: str})
		self.maxJobs = metadata.pop('MaxJobs')
		self.classname = metadata.pop('ClassName')
		self.metadata = {'None': dict(ifilter(lambda k_v: not k_v[0].startswith('['), metadata.items()))}
		for (k, v) in ifilter(lambda k_v: k_v[0].startswith('['), metadata.items()):
			self.metadata.setdefault('None %s' % k.split(']')[0].lstrip('['), {})[k.split(']')[1].strip()] = v
		del log


class DataSplitterIOAuto(DataSplitterIO):
	def saveState(self, path, meta, source, sourceLen, message = 'Writing job mapping file', version = 2):
		if version == 1:
			writer = DataSplitterIO_V1()
		else:
			writer = DataSplitterIO_V2()
		writer.saveState(path, meta, source, sourceLen, message)

	def loadState(self, path):
		try:
			version = int(tarfile.open(path, 'r:').extractfile('Version').read())
		except Exception:
			version = 1
		if version == 1:
			state = DataSplitterIO_V1().loadState(path)
		else:
			state = DataSplitterIO_V2().loadState(path)
		return state


class DataSplitterIO_V1(object):
	# Save as tar file to allow random access to mapping data with little memory overhead
	def saveState(self, path, meta, source, sourceLen, message):
		tar = tarfile.open(path, 'w:')
		fmt = utils.DictFormat()

		# Function to close all tarfiles
		def closeSubTar(jobNum, subTarFile, subTarFileObj):
			if subTarFile:
				subTarFile.close()
				try: # Python 3.2 does not close the wrapping gzip file object if an external file object is given
					subTarFile.fileobj.close()
				except Exception:
					pass
				subTarFileObj.seek(0)
				subTarFileInfo = tarfile.TarInfo('%03dXX.tgz' % (jobNum / 100))
				subTarFileInfo.size = len(subTarFileObj.getvalue())
				tar.addfile(subTarFileInfo, subTarFileObj)
		# Write the splitting info grouped into subtarfiles
		log = None
		(jobNum, subTarFile, subTarFileObj) = (-1, None, None)
		for jobNum, entry in enumerate(source):
			if jobNum % 100 == 0:
				closeSubTar(jobNum - 1, subTarFile, subTarFileObj)
				subTarFileObj = BytesBuffer()
				subTarFile = tarfile.open(mode = 'w:gz', fileobj = subTarFileObj)
				del log
				log = utils.ActivityLog('%s [%d / %d]' % (message, jobNum, sourceLen))
			# Determine shortest way to store file list
			tmp = entry.pop(DataSplitter.FileList)
			commonprefix = os.path.commonprefix(tmp)
			commonprefix = str.join('/', commonprefix.split('/')[:-1])
			if len(commonprefix) > 6:
				entry[DataSplitter.CommonPrefix] = commonprefix
				savelist = lmap(lambda x: x.replace(commonprefix + '/', ''), tmp)
			else:
				savelist = tmp
			# Write files with infos / filelist
			def flat(k_s_v):
				(x, y, z) = k_s_v
				if x in [DataSplitter.Metadata, DataSplitter.MetadataHeader]:
					return (x, y, repr(z))
				elif isinstance(z, list):
					return (x, y, str.join(',', z))
				return (x, y, z)
			for name, data in [('list', str.join('\n', savelist)), ('info', fmt.format(entry, fkt = flat))]:
				info, file = VirtualFile(os.path.join('%05d' % jobNum, name), data).getTarInfo()
				subTarFile.addfile(info, file)
				file.close()
			# Remove common prefix from info
			if DataSplitter.CommonPrefix in entry:
				entry.pop(DataSplitter.CommonPrefix)
			entry[DataSplitter.FileList] = tmp
		closeSubTar(jobNum, subTarFile, subTarFileObj)
		del log
		# Write metadata to allow reconstruction of data splitter
		meta['MaxJobs'] = jobNum + 1
		info, file = VirtualFile('Metadata', fmt.format(meta)).getTarInfo()
		tar.addfile(info, file)
		file.close()
		tar.close()


	def loadState(self, path):
		class JobFileTarAdaptor_V1(BaseJobFileTarAdaptor):
			def __getitem__(self, key):
				self._mutex.acquire()
				if not self._cacheKey == key / 100:
					self._cacheKey = key / 100
					subTarFileObj = self._tar.extractfile('%03dXX.tgz' % (key / 100))
					subTarFileObj = BytesBuffer(gzip.GzipFile(fileobj = subTarFileObj).read()) # 3-4x speedup for sequential access
					self._cacheTar = tarfile.open(mode = 'r', fileobj = subTarFileObj)
				parserMap = { None: str, DataSplitter.NEntries: int, DataSplitter.Skipped: int, 
					DataSplitter.DatasetID: int, DataSplitter.Invalid: utils.parseBool,
					DataSplitter.Locations: lambda x: parseList(x, ','), DataSplitter.MetadataHeader: eval,
					DataSplitter.Metadata: lambda x: eval(x.strip("'")) }
				data = self._fmt.parse(self._cacheTar.extractfile('%05d/info' % key).readlines(),
					keyParser = {None: int}, valueParser = parserMap)
				fileList = self._cacheTar.extractfile('%05d/list' % key).readlines()
				if DataSplitter.CommonPrefix in data:
					fileList = imap(lambda x: '%s/%s' % (data[DataSplitter.CommonPrefix], x), fileList)
				data[DataSplitter.FileList] = lmap(str.strip, fileList)
				self._mutex.release()
				return data

		try:
			return JobFileTarAdaptor_V1(path)
		except Exception:
			raise ConfigError("No valid dataset splitting found in '%s'." % path)

class DataSplitterIO_V2(object):
	def __init__(self):
		self.keySize = 100

	# Save as tar file to allow random access to mapping data with little memory overhead
	def saveState(self, path, meta, source, sourceLen, message):
		tar = tarfile.open(path, 'w:')
		fmt = utils.DictFormat()

		# Function to close all tarfiles
		def closeSubTar(jobNum, subTarFile, subTarFileObj):
			if subTarFile:
				subTarFile.close()
				try: # Python 3.2 does not close the wrapping gzip file object if an external file object is given
					subTarFile.fileobj.close()
				except Exception:
					pass
				subTarFileObj.seek(0)
				subTarFileInfo = tarfile.TarInfo('%03dXX.tgz' % (jobNum / self.keySize))
				subTarFileInfo.size = len(subTarFileObj.getvalue())
				tar.addfile(subTarFileInfo, subTarFileObj)
		# Write the splitting info grouped into subtarfiles
		log = None
		(jobNum, lastValid, subTarFile, subTarFileObj) = (-1, -1, None, None)
		for jobNum, entry in enumerate(source):
			if not entry.get(DataSplitter.Invalid, False):
				lastValid = jobNum
			if jobNum % self.keySize == 0:
				closeSubTar(jobNum - 1, subTarFile, subTarFileObj)
				subTarFileObj = BytesBuffer()
				subTarFile = tarfile.open(mode = 'w:gz', fileobj = subTarFileObj)
				del log
				log = utils.ActivityLog('%s [%d / %d]' % (message, jobNum, sourceLen))
			# Determine shortest way to store file list
			tmp = entry.pop(DataSplitter.FileList)
			commonprefix = os.path.commonprefix(tmp)
			commonprefix = str.join('/', commonprefix.split('/')[:-1])
			if len(commonprefix) > 6:
				entry[DataSplitter.CommonPrefix] = commonprefix
				savelist = lmap(lambda x: x.replace(commonprefix + '/', ''), tmp)
			else:
				savelist = tmp
			# Write files with infos / filelist
			def flat(k_s_v):
				(x, y, z) = k_s_v
				if x in [DataSplitter.Metadata, DataSplitter.MetadataHeader]:
					return (x, y, repr(z))
				elif isinstance(z, list):
					return (x, y, str.join(',', z))
				return (x, y, z)
			data = str.join('', fmt.format(entry, fkt = flat) + lmap(lambda fn: '=%s\n' % fn, savelist))
			info, file = VirtualFile('%05d' % jobNum, data).getTarInfo()
			subTarFile.addfile(info, file)
			file.close()
			# Remove common prefix from info
			if DataSplitter.CommonPrefix in entry:
				entry.pop(DataSplitter.CommonPrefix)
			entry[DataSplitter.FileList] = tmp
		closeSubTar(jobNum, subTarFile, subTarFileObj)
		del log
		# Write metadata to allow reconstruction of data splitter
		meta['MaxJobs'] = lastValid + 1
		for (fn, data) in [('Metadata', fmt.format(meta)), ('Version', '2')]:
			info, file = VirtualFile(fn, data).getTarInfo()
			tar.addfile(info, file)
			file.close()
		tar.close()


	def loadState(self, path):
		class JobFileTarAdaptor_V2(BaseJobFileTarAdaptor):
			def __init__(self, path, keySize):
				BaseJobFileTarAdaptor.__init__(self, path)
				self.keySize = keySize

			def __getitem__(self, key):
				if key >= self.maxJobs:
					raise IndexError
				self._mutex.acquire()
				if not self._cacheKey == key / self.keySize:
					self._cacheKey = key / self.keySize
					subTarFileObj = self._tar.extractfile('%03dXX.tgz' % (key / self.keySize))
					subTarFileObj = BytesBuffer(gzip.GzipFile(fileobj = subTarFileObj).read()) # 3-4x speedup for sequential access
					self._cacheTar = tarfile.open(mode = 'r', fileobj = subTarFileObj)
				parserMap = { None: str, DataSplitter.NEntries: int, DataSplitter.Skipped: int, 
					DataSplitter.DatasetID: int, DataSplitter.Invalid: utils.parseBool,
					DataSplitter.Locations: lambda x: parseList(x, ','), DataSplitter.MetadataHeader: eval,
					DataSplitter.Metadata: lambda x: eval(x.strip("'")) }
				fullData = lmap(bytes2str, self._cacheTar.extractfile('%05d' % key).readlines())
				data = self._fmt.parse(lfilter(lambda x: not x.startswith('='), fullData),
					keyParser = {None: int}, valueParser = parserMap)
				fileList = imap(lambda x: x[1:], ifilter(lambda x: x.startswith('='), fullData))
				if DataSplitter.CommonPrefix in data:
					fileList = imap(lambda x: '%s/%s' % (data[DataSplitter.CommonPrefix], x), fileList)
				data[DataSplitter.FileList] = lmap(str.strip, fileList)
				self._mutex.release()
				return data

		try:
			return JobFileTarAdaptor_V2(path, self.keySize)
		except Exception:
			raise ConfigError("No valid dataset splitting found in '%s'." % path)
