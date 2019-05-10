# /******************************************************************************
#  * Copyright 2013 VMware, Inc.  All rights reserved.
#  *
#  *      Contains function declarations for mounting VMDK files.
#  *
#  *******************************************************************************/

import sys
from pyvddk import *


VIXMNTAPI_MAJOR_VERSION       =     1
VIXMNTAPI_MINOR_VERSION       =     0

# /**
#  * OS Family types - Currently, only Windows OS is recognized.
#  */
VIXMNTAPI_NO_OS               =     0
VIXMNTAPI_WINDOWS             =     1
VIXMNTAPI_OTHER               =     255

# /**
#  * Information about the default OS installed on the disks. Windows only.
#  */
class VixOsInfo(Structure):
   _fields_ = [
      ("family", c_int),        # OS Family
      ("majorVersion", c_uint), # On Windows, 4=NT, 5=2000 and above
      ("minorVersion", c_uint), # On Windows, 0=2000, 1=XP, 2=2003
      ("osis64Bit", c_ushort),  # True if the OS is 64-bit
      ("vendor", c_char_p),     # // e.g. Microsoft, RedHat, etc ...
      ("edition", c_char_p),    # // e.g. Desktop, Enterprise, etc ...
      ("osFolder", c_char_p),   # // Location where the default OS is installed
   ]

# /**
#  * Type of the volume.
#  */
VIXMNTAPI_UNKNOWN_VOLTYPE      = 0
VIXMNTAPI_BASIC_PARTITION      = 1
VIXMNTAPI_GPT_PARTITION        = 2
VIXMNTAPI_DYNAMIC_VOLUME       = 3
VIXMNTAPI_LVM_VOLUME           = 4

# /**
#  * Volume information.
#  */
class VixVolumeInfo(Structure):
   _fields_ = [
   ("type", c_int), # // Type of the volume
   ("isMounted", c_ushort), # // True if the volume is mounted on the proxy.
   ("symbolicLink", c_char_p), # // Path to the volume mount point,
   ("numGuestMountPoints", c_ulonglong), #        // Number of mount points for the volume in the guest
   ("inGuestMountPoints", POINTER(c_char_p)) # [1];        // Mount points for the volume in the guest
   ]

class VixDiskSetInfo(Structure):
   _fields_ = [
   ("openFlags", c_uint),
   ("mountPath", c_char_p),
   ]

class VixDiskSetHandleStruct(Structure):
   pass

class VixVolumeHandleStruct(Structure):
   pass

VixDiskSetHandle = POINTER(VixDiskSetHandleStruct)
VixVolumeHandle = POINTER(VixVolumeHandleStruct)

LOGGERTYPE = CFUNCTYPE(None, c_char_p)

_initApi = None
_mntApi = None

def InitApi():
   global _initApi
   if not _initApi:
      try:
         _initApi = CDLL(os.path.abspath('libvixDiskLibTest.so'))
      except:
         _initApi = CDLL('vixDiskLibTest.dll')
   return _initApi

def MntApi():
   global _mntApi
   if not _mntApi:
      try:
         _mntApi = CDLL('libvixMntapi.so')
      except:
         _mntApi = CDLL('vixMntapi.dll')
   return _mntApi

if sys.platform == 'win32':
   MntApi().VixMntapi_OpenDiskSet.restype = c_ulonglong
   MntApi().VixMntapi_OpenDiskSet.argtypes = [POINTER(VixDiskLibHandle), c_uint64, c_uint, POINTER(VixDiskSetHandle)]

InitApi().VixMntapiTest_Init.restype = c_ulonglong
InitApi().VixMntapiTest_Init.argtypes = [c_uint, c_uint, LOGGERTYPE, LOGGERTYPE, LOGGERTYPE, c_char_p, c_char_p]
MntApi().VixMntapi_Exit.restype = None
MntApi().VixMntapi_Exit.argtypes = []
MntApi().VixMntapi_OpenDisks.restype = c_ulonglong
MntApi().VixMntapi_OpenDisks.argtypes = [VixDiskLibConnection, POINTER(c_char_p), c_uint64, c_uint, POINTER(VixDiskSetHandle)]
MntApi().VixMntapi_GetDiskSetInfo.restype = c_ulonglong
MntApi().VixMntapi_GetDiskSetInfo.argtypes = [VixDiskSetHandle, POINTER(POINTER(VixDiskSetInfo))]
MntApi().VixMntapi_FreeDiskSetInfo.restype = None
MntApi().VixMntapi_FreeDiskSetInfo.argtypes = [POINTER(VixDiskSetInfo)]
MntApi().VixMntapi_CloseDiskSet.restype = c_ulonglong
MntApi().VixMntapi_CloseDiskSet.argtypes = [VixDiskSetHandle]
MntApi().VixMntapi_GetVolumeHandles.restype = c_ulonglong
MntApi().VixMntapi_GetVolumeHandles.argtypes = [VixDiskSetHandle, POINTER(c_uint64), POINTER(c_void_p)]
MntApi().VixMntapi_FreeVolumeHandles.restype = None
MntApi().VixMntapi_FreeVolumeHandles.argtypes = [POINTER(VixVolumeHandle)]
MntApi().VixMntapi_GetOsInfo.restype = c_ulonglong
MntApi().VixMntapi_GetOsInfo.argtypes = [VixDiskSetHandle, POINTER(POINTER(VixOsInfo))]
MntApi().VixMntapi_FreeOsInfo.restype = None
MntApi().VixMntapi_FreeOsInfo.argtypes = [POINTER(VixOsInfo)]
MntApi().VixMntapi_MountVolume.restype = c_ulonglong
MntApi().VixMntapi_MountVolume.argtypes = [VixVolumeHandle, c_uint16]
MntApi().VixMntapi_DismountVolume.restype = c_ulonglong
MntApi().VixMntapi_DismountVolume.argtypes = [VixVolumeHandle, c_uint16]
MntApi().VixMntapi_GetVolumeInfo.restype = c_ulonglong
MntApi().VixMntapi_GetVolumeInfo.argtypes = [VixVolumeHandle, POINTER(POINTER(VixVolumeInfo))]
MntApi().VixMntapi_FreeVolumeInfo.restype = None
MntApi().VixMntapi_FreeVolumeInfo.argtypes = [POINTER(VixVolumeInfo)]


def Init(majorVersion, minorVersion, logCb, warnCb, panicCb, libDir, configFile):
   args = []
   for cb in (logCb, warnCb, panicCb):
      if cb:
         cb.handle = LOGGERTYPE(cb)
         args.append(cb.handle)
      else:
         args.append(None)
   res = InitApi().VixMntapiTest_Init(majorVersion, minorVersion,
                                      args[0], args[1], args[2],
                                      libDir, configFile)
   if VIX_FAILED(res):
      raise VixDiskLibException(res, "Failed to call VixMntapiTest_Init()")

def ApiThunk(apiName, *args):
   api = MntApi()
   method = getattr(api, apiName)
   if method.restype != None:
      res = method(*args)
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Failed to call %s", apiName)
   else:
      method(*args)

def Exit():
   ApiThunk("VixMntapi_Exit")


class VixVolume(object):
   def __init__(self, handle):
      self._handle = handle

   def Mount(self, readOnly):
      ApiThunk("VixMntapi_MountVolume", self._handle, readOnly)

   def Dismount(self, force):
      ApiThunk("VixMntapi_DismountVolume", self._handle, force)

   def GetVolumeInfo(self):
      volInfo = POINTER(VixVolumeInfo)()
      ApiThunk("VixMntapi_GetVolumeInfo", self._handle, pointer(volInfo))
      d = {}
      for field in ["type", \
                    "isMounted", \
                    "symbolicLink", \
                    "numGuestMountPoints"]:
         d[field] = getattr(volInfo.contents, field)

      mountPoints = POINTER(c_char_p)(volInfo.contents.inGuestMountPoints)
      mp = []
      for n in range(d['numGuestMountPoints']):
         mp.append(mountPoints[0].contents)
      d['inGuestMountPoints'] = mp
      return d


class DiskSet(object):
   def __init__(self, handle):
      self._handle = handle
      self._volHandles = None

   def GetInfo(self):
      infop = POINTER(VixDiskSetInfo)()
      res = {}
      ApiThunk("VixMntapi_GetDiskSetInfo", self._handle, byref(infop))
      # use infop
      res['openFlags'] = infop.contents.openFlags
      res['mountPath'] = infop.contents.mountPath
      ApiThunk("VixMntapi_FreeDiskSetInfo", infop)
      return res

   def GetOsInfo(self):
      infop = POINTER(VixOsInfo)()
      res = {}
      ApiThunk("VixMntapi_GetOsInfo", self._handle, byref(infop))
      for field in ["family", \
                    "majorVersion", \
                    "minorVersion", \
                    "osis64Bit", \
                    "vendor", \
                    "edition", \
                    "osFolder"]:
         res[field] = getattr(infop.contents, field)
      ApiThunk("VixMntapi_FreeOsInfo", infop)
      return res


   def Close(self):
      ApiThunk("VixMntapi_CloseDiskSet", self._handle)
      self._handle = None

   def GetVolumeHandles(self):
      if self._volHandles != None:
         raise VixDiskLibException(VIX_E_FAIL, "Need to free previous volHandles")
      count = c_uint64()
      handleArray = c_void_p()
      ApiThunk("VixMntapi_GetVolumeHandles", self._handle, byref(count), byref(handleArray))
      count = count.value
      res = []
      newArray = VixVolumeHandle * count
      handleArray = newArray.from_address(handleArray.value)
      # print "XXX--- %s" % handleArray.contents
      for i in range(count):
         volHandle = handleArray[i]
         res.append(VixVolume(volHandle))
      self._volHandles = handleArray
      return res

   def DestroyVolumeHandles(self):
      ApiThunk("VixMntapi_FreeVolumeHandles", self._volHandles)
      self._volHandles = None



class VixMntapi(object):
   def __init__(self):
      self._params = None
      self._connPtr = None

   def OpenDisks(self, connection, diskNames, openFlags):
      handle = VixDiskSetHandle()
      cNames = (c_char_p * len(diskNames))(*diskNames)
      ApiThunk("VixMntapi_OpenDisks", connection, cNames, len(diskNames),
               openFlags, byref(handle))
      return DiskSet(handle)

   def OpenDiskSet(self, handles, openMode):
      if sys.platform != 'win32':
         raise VixDiskLibException(VIX_E_FAIL, "OpenDiskSet only supported on win32!")
      handle = VixDiskSetHandle()
      cHandles = (c_void_p * len(handles))(*handles)
      ApiThunk("VixMntapi_OpenDiskSet", cHandles, len(handles),
               openMode, byref(handle))
      return DiskSet(handle)
