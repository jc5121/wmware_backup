###################################################
# Copyright 2012-2016 VMware, Inc.  All rights reserved. -- VMware Confidential
###################################################


__doc__ = "A bare-bones wrapper around the vixdisklib api"
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl

from ctypes import *
import os
import exceptions
import sys

c_uint_p = POINTER(c_uint)

def VIX_ERROR_CODE(err):
   return err & 0xFFFF
def VIX_SUCCEEDED(err):
   return VIX_OK == err
def VIX_FAILED(err):
   return VIX_OK != err

VIX_OK                                       = 0

# /* General errors */
VIX_E_FAIL                                   = 1
VIX_E_OUT_OF_MEMORY                          = 2
VIX_E_INVALID_ARG                            = 3
VIX_E_FILE_NOT_FOUND                         = 4
VIX_E_OBJECT_IS_BUSY                         = 5
VIX_E_NOT_SUPPORTED                          = 6
VIX_E_FILE_ERROR                             = 7
VIX_E_DISK_FULL                              = 8
VIX_E_INCORRECT_FILE_TYPE                    = 9
VIX_E_CANCELLED                              = 10
VIX_E_FILE_READ_ONLY                         = 11
VIX_E_FILE_ALREADY_EXISTS                    = 12
VIX_E_FILE_ACCESS_ERROR                      = 13
VIX_E_REQUIRES_LARGE_FILES                   = 14
VIX_E_FILE_ALREADY_LOCKED                    = 15
VIX_E_VMDB                                   = 16
VIX_E_NOT_SUPPORTED_ON_REMOTE_OBJECT         = 20
VIX_E_FILE_TOO_BIG                           = 21
VIX_E_FILE_NAME_INVALID                      = 22
VIX_E_ALREADY_EXISTS                         = 23
VIX_E_BUFFER_TOOSMALL                        = 24
VIX_E_OBJECT_NOT_FOUND                       = 25
VIX_E_HOST_NOT_CONNECTED                     = 26
VIX_E_INVALID_UTF8_STRING                    = 27
VIX_E_OPERATION_ALREADY_IN_PROGRESS          = 31
VIX_E_UNFINISHED_JOB                         = 29
VIX_E_NEED_KEY                               = 30
VIX_E_LICENSE                                = 32
VIX_E_VM_HOST_DISCONNECTED                   = 34
VIX_E_AUTHENTICATION_FAIL                    = 35
VIX_E_HOST_CONNECTION_LOST                   = 36
VIX_E_DUPLICATE_NAME                         = 41

# /* Handle Errors */
VIX_E_INVALID_HANDLE                         = 1000
VIX_E_NOT_SUPPORTED_ON_HANDLE_TYPE           = 1001
VIX_E_TOO_MANY_HANDLES                       = 1002

# /* XML errors */
VIX_E_NOT_FOUND                              = 2000
VIX_E_TYPE_MISMATCH                          = 2001
VIX_E_INVALID_XML                            = 2002

# /* VM Control Errors */
VIX_E_TIMEOUT_WAITING_FOR_TOOLS              = 3000
VIX_E_UNRECOGNIZED_COMMAND                   = 3001
VIX_E_OP_NOT_SUPPORTED_ON_GUEST              = 3003
VIX_E_PROGRAM_NOT_STARTED                    = 3004
VIX_E_CANNOT_START_READ_ONLY_VM              = 3005
VIX_E_VM_NOT_RUNNING                         = 3006
VIX_E_VM_IS_RUNNING                          = 3007
VIX_E_CANNOT_CONNECT_TO_VM                   = 3008
VIX_E_POWEROP_SCRIPTS_NOT_AVAILABLE          = 3009
VIX_E_NO_GUEST_OS_INSTALLED                  = 3010
VIX_E_VM_INSUFFICIENT_HOST_MEMORY            = 3011
VIX_E_SUSPEND_ERROR                          = 3012
VIX_E_VM_NOT_ENOUGH_CPUS                     = 3013
VIX_E_HOST_USER_PERMISSIONS                  = 3014
VIX_E_GUEST_USER_PERMISSIONS                 = 3015
VIX_E_TOOLS_NOT_RUNNING                      = 3016
VIX_E_GUEST_OPERATIONS_PROHIBITED            = 3017
VIX_E_ANON_GUEST_OPERATIONS_PROHIBITED       = 3018
VIX_E_ROOT_GUEST_OPERATIONS_PROHIBITED       = 3019
VIX_E_MISSING_ANON_GUEST_ACCOUNT             = 3023
VIX_E_CANNOT_AUTHENTICATE_WITH_GUEST         = 3024
VIX_E_UNRECOGNIZED_COMMAND_IN_GUEST          = 3025
VIX_E_CONSOLE_GUEST_OPERATIONS_PROHIBITED    = 3026
VIX_E_MUST_BE_CONSOLE_USER                   = 3027
VIX_E_VMX_MSG_DIALOG_AND_NO_UI               = 3028
# /* VIX_E_NOT_ALLOWED_DURING_VM_RECORDING        = 3029 Removed in version 1.11 */
# /* VIX_E_NOT_ALLOWED_DURING_VM_REPLAY           = 3030 Removed in version 1.11 */
VIX_E_OPERATION_NOT_ALLOWED_FOR_LOGIN_TYPE   = 3031
VIX_E_LOGIN_TYPE_NOT_SUPPORTED               = 3032
VIX_E_EMPTY_PASSWORD_NOT_ALLOWED_IN_GUEST    = 3033
VIX_E_INTERACTIVE_SESSION_NOT_PRESENT        = 3034
VIX_E_INTERACTIVE_SESSION_USER_MISMATCH      = 3035
# /* VIX_E_UNABLE_TO_REPLAY_VM                    = 3039 Removed in version 1.11 */
VIX_E_CANNOT_POWER_ON_VM                     = 3041
VIX_E_NO_DISPLAY_SERVER                      = 3043
# /* VIX_E_VM_NOT_RECORDING                       = 3044 Removed in version 1.11 */
# /* VIX_E_VM_NOT_REPLAYING                       = 3045 Removed in version 1.11 */
VIX_E_TOO_MANY_LOGONS                        = 3046
VIX_E_INVALID_AUTHENTICATION_SESSION         = 3047

# /* VM Errors */
VIX_E_VM_NOT_FOUND                           = 4000
VIX_E_NOT_SUPPORTED_FOR_VM_VERSION           = 4001
VIX_E_CANNOT_READ_VM_CONFIG                  = 4002
VIX_E_TEMPLATE_VM                            = 4003
VIX_E_VM_ALREADY_LOADED                      = 4004
VIX_E_VM_ALREADY_UP_TO_DATE                  = 4006
VIX_E_VM_UNSUPPORTED_GUEST                   = 4011

# /* Property Errors */
VIX_E_UNRECOGNIZED_PROPERTY                  = 6000
VIX_E_INVALID_PROPERTY_VALUE                 = 6001
VIX_E_READ_ONLY_PROPERTY                     = 6002
VIX_E_MISSING_REQUIRED_PROPERTY              = 6003
VIX_E_INVALID_SERIALIZED_DATA                = 6004
VIX_E_PROPERTY_TYPE_MISMATCH                 = 6005

# /* Completion Errors */
VIX_E_BAD_VM_INDEX                           = 8000

# /* Message errors */
VIX_E_INVALID_MESSAGE_HEADER                 = 10000
VIX_E_INVALID_MESSAGE_BODY                   = 10001

# /* Snapshot errors */
VIX_E_SNAPSHOT_INVAL                         = 13000
VIX_E_SNAPSHOT_DUMPER                        = 13001
VIX_E_SNAPSHOT_DISKLIB                       = 13002
VIX_E_SNAPSHOT_NOTFOUND                      = 13003
VIX_E_SNAPSHOT_EXISTS                        = 13004
VIX_E_SNAPSHOT_VERSION                       = 13005
VIX_E_SNAPSHOT_NOPERM                        = 13006
VIX_E_SNAPSHOT_CONFIG                        = 13007
VIX_E_SNAPSHOT_NOCHANGE                      = 13008
VIX_E_SNAPSHOT_CHECKPOINT                    = 13009
VIX_E_SNAPSHOT_LOCKED                        = 13010
VIX_E_SNAPSHOT_INCONSISTENT                  = 13011
VIX_E_SNAPSHOT_NAMETOOLONG                   = 13012
VIX_E_SNAPSHOT_VIXFILE                       = 13013
VIX_E_SNAPSHOT_DISKLOCKED                    = 13014
VIX_E_SNAPSHOT_DUPLICATEDDISK                = 13015
VIX_E_SNAPSHOT_INDEPENDENTDISK               = 13016
VIX_E_SNAPSHOT_NONUNIQUE_NAME                = 13017
VIX_E_SNAPSHOT_MEMORY_ON_INDEPENDENT_DISK    = 13018
VIX_E_SNAPSHOT_MAXSNAPSHOTS                  = 13019
VIX_E_SNAPSHOT_MIN_FREE_SPACE                = 13020
VIX_E_SNAPSHOT_HIERARCHY_TOODEEP             = 13021
VIX_E_SNAPSHOT_RRSUSPEND                     = 13022
VIX_E_SNAPSHOT_NOT_REVERTABLE                = 13024

# /* Host Errors */
VIX_E_HOST_DISK_INVALID_VALUE                = 14003
VIX_E_HOST_DISK_SECTORSIZE                   = 14004
VIX_E_HOST_FILE_ERROR_EOF                    = 14005
VIX_E_HOST_NETBLKDEV_HANDSHAKE               = 14006
VIX_E_HOST_SOCKET_CREATION_ERROR             = 14007
VIX_E_HOST_SERVER_NOT_FOUND                  = 14008
VIX_E_HOST_NETWORK_CONN_REFUSED              = 14009
VIX_E_HOST_TCP_SOCKET_ERROR                  = 14010
VIX_E_HOST_TCP_CONN_LOST                     = 14011
VIX_E_HOST_NBD_HASHFILE_VOLUME               = 14012
VIX_E_HOST_NBD_HASHFILE_INIT                 = 14013

# /* Disklib errors */
VIX_E_DISK_INVAL                             = 16000
VIX_E_DISK_NOINIT                            = 16001
VIX_E_DISK_NOIO                              = 16002
VIX_E_DISK_PARTIALCHAIN                      = 16003
VIX_E_DISK_NEEDSREPAIR                       = 16006
VIX_E_DISK_OUTOFRANGE                        = 16007
VIX_E_DISK_CID_MISMATCH                      = 16008
VIX_E_DISK_CANTSHRINK                        = 16009
VIX_E_DISK_PARTMISMATCH                      = 16010
VIX_E_DISK_UNSUPPORTEDDISKVERSION            = 16011
VIX_E_DISK_OPENPARENT                        = 16012
VIX_E_DISK_NOTSUPPORTED                      = 16013
VIX_E_DISK_NEEDKEY                           = 16014
VIX_E_DISK_NOKEYOVERRIDE                     = 16015
VIX_E_DISK_NOTENCRYPTED                      = 16016
VIX_E_DISK_NOKEY                             = 16017
VIX_E_DISK_INVALIDPARTITIONTABLE             = 16018
VIX_E_DISK_NOTNORMAL                         = 16019
VIX_E_DISK_NOTENCDESC                        = 16020
VIX_E_DISK_NEEDVMFS                          = 16022
VIX_E_DISK_RAWTOOBIG                         = 16024
VIX_E_DISK_TOOMANYOPENFILES                  = 16027
VIX_E_DISK_TOOMANYREDO                       = 16028
VIX_E_DISK_RAWTOOSMALL                       = 16029
VIX_E_DISK_INVALIDCHAIN                      = 16030
VIX_E_DISK_KEY_NOTFOUND                      = 16052  # // metadata key is not found
VIX_E_DISK_SUBSYSTEM_INIT_FAIL               = 16053
VIX_E_DISK_INVALID_CONNECTION                = 16054
VIX_E_DISK_ENCODING                          = 16061
VIX_E_DISK_CANTREPAIR                        = 16062
VIX_E_DISK_INVALIDDISK                       = 16063
VIX_E_DISK_NOLICENSE                         = 16064
VIX_E_DISK_NODEVICE                          = 16065
VIX_E_DISK_UNSUPPORTEDDEVICE                 = 16066
VIX_E_DISK_CAPACITY_MISMATCH                 = 16067
VIX_E_DISK_PARENT_NOTALLOWED                 = 16068
VIX_E_DISK_ATTACH_ROOTLINK                   = 16069

# /* Crypto Library Errors */
VIX_E_CRYPTO_UNKNOWN_ALGORITHM               = 17000
VIX_E_CRYPTO_BAD_BUFFER_SIZE                 = 17001
VIX_E_CRYPTO_INVALID_OPERATION               = 17002
VIX_E_CRYPTO_RANDOM_DEVICE                   = 17003
VIX_E_CRYPTO_NEED_PASSWORD                   = 17004
VIX_E_CRYPTO_BAD_PASSWORD                    = 17005
VIX_E_CRYPTO_NOT_IN_DICTIONARY               = 17006
VIX_E_CRYPTO_NO_CRYPTO                       = 17007
VIX_E_CRYPTO_ERROR                           = 17008
VIX_E_CRYPTO_BAD_FORMAT                      = 17009
VIX_E_CRYPTO_LOCKED                          = 17010
VIX_E_CRYPTO_EMPTY                           = 17011
VIX_E_CRYPTO_KEYSAFE_LOCATOR                 = 17012

# /* Remoting Errors. */
VIX_E_CANNOT_CONNECT_TO_HOST                 = 18000
VIX_E_NOT_FOR_REMOTE_HOST                    = 18001
VIX_E_INVALID_HOSTNAME_SPECIFICATION         = 18002

# /* Screen Capture Errors. */
VIX_E_SCREEN_CAPTURE_ERROR                   = 19000
VIX_E_SCREEN_CAPTURE_BAD_FORMAT              = 19001
VIX_E_SCREEN_CAPTURE_COMPRESSION_FAIL        = 19002
VIX_E_SCREEN_CAPTURE_LARGE_DATA              = 19003

# /* Guest Errors */
VIX_E_GUEST_VOLUMES_NOT_FROZEN               = 20000
VIX_E_NOT_A_FILE                             = 20001
VIX_E_NOT_A_DIRECTORY                        = 20002
VIX_E_NO_SUCH_PROCESS                        = 20003
VIX_E_FILE_NAME_TOO_LONG                     = 20004
VIX_E_OPERATION_DISABLED                     = 20005

# /* Tools install errors */
VIX_E_TOOLS_INSTALL_NO_IMAGE                 = 21000
VIX_E_TOOLS_INSTALL_IMAGE_INACCESIBLE        = 21001
VIX_E_TOOLS_INSTALL_NO_DEVICE                = 21002
VIX_E_TOOLS_INSTALL_DEVICE_NOT_CONNECTED     = 21003
VIX_E_TOOLS_INSTALL_CANCELLED                = 21004
VIX_E_TOOLS_INSTALL_INIT_FAILED              = 21005
VIX_E_TOOLS_INSTALL_AUTO_NOT_SUPPORTED       = 21006
VIX_E_TOOLS_INSTALL_GUEST_NOT_READY          = 21007
VIX_E_TOOLS_INSTALL_SIG_CHECK_FAILED         = 21008
VIX_E_TOOLS_INSTALL_ERROR                    = 21009
VIX_E_TOOLS_INSTALL_ALREADY_UP_TO_DATE       = 21010
VIX_E_TOOLS_INSTALL_IN_PROGRESS              = 21011
VIX_E_TOOLS_INSTALL_IMAGE_COPY_FAILED        = 21012

# /* Wrapper Errors */
VIX_E_WRAPPER_WORKSTATION_NOT_INSTALLED      = 22001
VIX_E_WRAPPER_VERSION_NOT_FOUND              = 22002
VIX_E_WRAPPER_SERVICEPROVIDER_NOT_FOUND      = 22003
VIX_E_WRAPPER_PLAYER_NOT_INSTALLED           = 22004
VIX_E_WRAPPER_RUNTIME_NOT_INSTALLED          = 22005
VIX_E_WRAPPER_MULTIPLE_SERVICEPROVIDERS      = 22006

# /* FuseMnt errors*/
VIX_E_MNTAPI_MOUNTPT_NOT_FOUND               = 24000
VIX_E_MNTAPI_MOUNTPT_IN_USE                  = 24001
VIX_E_MNTAPI_DISK_NOT_FOUND                  = 24002
VIX_E_MNTAPI_DISK_NOT_MOUNTED                = 24003
VIX_E_MNTAPI_DISK_IS_MOUNTED                 = 24004
VIX_E_MNTAPI_DISK_NOT_SAFE                   = 24005
VIX_E_MNTAPI_DISK_CANT_OPEN                  = 24006
VIX_E_MNTAPI_CANT_READ_PARTS                 = 24007
VIX_E_MNTAPI_UMOUNT_APP_NOT_FOUND            = 24008
VIX_E_MNTAPI_UMOUNT                          = 24009
VIX_E_MNTAPI_NO_MOUNTABLE_PARTITONS          = 24010
VIX_E_MNTAPI_PARTITION_RANGE                 = 24011
VIX_E_MNTAPI_PERM                            = 24012
VIX_E_MNTAPI_DICT                            = 24013
VIX_E_MNTAPI_DICT_LOCKED                     = 24014
VIX_E_MNTAPI_OPEN_HANDLES                    = 24015
VIX_E_MNTAPI_CANT_MAKE_VAR_DIR               = 24016
VIX_E_MNTAPI_NO_ROOT                         = 24017
VIX_E_MNTAPI_LOOP_FAILED                     = 24018
VIX_E_MNTAPI_DAEMON                          = 24019
VIX_E_MNTAPI_INTERNAL                        = 24020
VIX_E_MNTAPI_SYSTEM                          = 24021
VIX_E_MNTAPI_NO_CONNECTION_DETAILS           = 24022
# /* FuseMnt errors: Do not exceed 24299 */

# /* VixMntapi errors*/
VIX_E_MNTAPI_INCOMPATIBLE_VERSION            = 24300
VIX_E_MNTAPI_OS_ERROR                        = 24301
VIX_E_MNTAPI_DRIVE_LETTER_IN_USE             = 24302
VIX_E_MNTAPI_DRIVE_LETTER_ALREADY_ASSIGNED   = 24303
VIX_E_MNTAPI_VOLUME_NOT_MOUNTED              = 24304
VIX_E_MNTAPI_VOLUME_ALREADY_MOUNTED          = 24305
VIX_E_MNTAPI_FORMAT_FAILURE                  = 24306
VIX_E_MNTAPI_NO_DRIVER                       = 24307
VIX_E_MNTAPI_ALREADY_OPENED                  = 24308
VIX_E_MNTAPI_ITEM_NOT_FOUND                  = 24309
VIX_E_MNTAPI_UNSUPPROTED_BOOT_LOADER         = 24310
VIX_E_MNTAPI_UNSUPPROTED_OS                  = 24311
VIX_E_MNTAPI_CODECONVERSION                  = 24312
VIX_E_MNTAPI_REGWRITE_ERROR                  = 24313
VIX_E_MNTAPI_UNSUPPORTED_FT_VOLUME           = 24314
VIX_E_MNTAPI_PARTITION_NOT_FOUND             = 24315
VIX_E_MNTAPI_PUTFILE_ERROR                   = 24316
VIX_E_MNTAPI_GETFILE_ERROR                   = 24317
VIX_E_MNTAPI_REG_NOT_OPENED                  = 24318
VIX_E_MNTAPI_REGDELKEY_ERROR                 = 24319
VIX_E_MNTAPI_CREATE_PARTITIONTABLE_ERROR     = 24320
VIX_E_MNTAPI_OPEN_FAILURE                    = 24321
VIX_E_MNTAPI_VOLUME_NOT_WRITABLE             = 24322

# /* Network Errors */
VIX_E_NET_HTTP_UNSUPPORTED_PROTOCOL     = 30001
VIX_E_NET_HTTP_URL_MALFORMAT            = 30003
VIX_E_NET_HTTP_COULDNT_RESOLVE_PROXY    = 30005
VIX_E_NET_HTTP_COULDNT_RESOLVE_HOST     = 30006
VIX_E_NET_HTTP_COULDNT_CONNECT          = 30007
VIX_E_NET_HTTP_HTTP_RETURNED_ERROR      = 30022
VIX_E_NET_HTTP_OPERATION_TIMEDOUT       = 30028
VIX_E_NET_HTTP_SSL_CONNECT_ERROR        = 30035
VIX_E_NET_HTTP_TOO_MANY_REDIRECTS       = 30047
VIX_E_NET_HTTP_TRANSFER                 = 30200
VIX_E_NET_HTTP_SSL_SECURITY             = 30201
VIX_E_NET_HTTP_GENERIC                  = 30202



VIXDISKLIB_SECTOR_SIZE                  = 512

class VixDiskLibGeometry(Structure):
   _fields_ = [
      ('cylinders',  c_uint),
      ('heads',  c_uint),
      ('sectors',  c_uint),
   ]

VIXDISKLIB_DISK_MONOLITHIC_SPARSE         = 1    # // monolithic file, sparse
VIXDISKLIB_DISK_MONOLITHIC_FLAT           = 2    # // monolithic file,
                                                 # // all space pre-allocated
VIXDISKLIB_DISK_SPLIT_SPARSE              = 3    # // disk split into 2GB extents,
                                                 # // sparse
VIXDISKLIB_DISK_SPLIT_FLAT                = 4    # // disk split into 2GB extents,
                                                 # // pre-allocated
VIXDISKLIB_DISK_VMFS_FLAT                 = 5    # // ESX 3.0 and above flat disks
VIXDISKLIB_DISK_STREAM_OPTIMIZED          = 6    # // compressed monolithic sparse
VIXDISKLIB_DISK_VMFS_THIN                 = 7    # // ESX 3.0 and above thin provisioned
VIXDISKLIB_DISK_VMFS_SPARSE               = 8    # // ESX 3.0 and above sparse disks
VIXDISKLIB_DISK_UNKNOWN                   = 256  # // unknown type

VIXDISKLIB_ADAPTER_IDE                    = 1
VIXDISKLIB_ADAPTER_SCSI_BUSLOGIC          = 2
VIXDISKLIB_ADAPTER_SCSI_LSILOGIC          = 3
VIXDISKLIB_ADAPTER_UNKNOWN                = 256


VIXDISKLIB_HWVERSION_WORKSTATION_4        = 3

# // VMware Workstation 5.x and Server 1.x
VIXDISKLIB_HWVERSION_WORKSTATION_5        = 4

# // VMware Workstation 6.x
VIXDISKLIB_HWVERSION_WORKSTATION_6        = 6

# // VMware vSphere versions
VIXDISKLIB_HWVERSION_ESX30                = VIXDISKLIB_HWVERSION_WORKSTATION_5
VIXDISKLIB_HWVERSION_ESX4X                = 7
VIXDISKLIB_HWVERSION_ESX50                = 8
VIXDISKLIB_HWVERSION_ESX51                = 9
VIXDISKLIB_HWVERSION_ESX55                = 10

# /*
#  * Defines the state of the art hardware version.  Be careful using this as it
#  * will change from time to time.
#  */

VIXDISKLIB_HWVERSION_CURRENT              = VIXDISKLIB_HWVERSION_ESX55


class VixDiskLibCreateParams(Structure):
   _fields_ = [
      ("diskType", c_int),
      ("adapterType", c_int),
      ("hwVersion", c_ushort),
      ("capacity", c_ulonglong),
   ]


VIXDISKLIB_CRED_UID                      = 1 # // use userid password
VIXDISKLIB_CRED_SESSIONID                = 2 # // http session id
VIXDISKLIB_CRED_TICKETID                 = 3 # // vim ticket id
VIXDISKLIB_CRED_SSPI                     = 4 # // Windows only - use current thread credentials.
VIXDISKLIB_CRED_UNKNOWN                  = 256


class VixDiskLibUidPasswdCreds(Structure):
   _fields_ = [
      ("userName", c_char_p),
      ("password", c_char_p),
   ]

class VixDiskLibSessionIdCreds(Structure):
   _fields_ = [
      ("cookie", c_char_p),
      ("userName", c_char_p),
      ("key", c_char_p),
   ]

class VixDiskLibCreds(Union):
   _fields_ = [
      ("uid", VixDiskLibUidPasswdCreds),
      ("sessionId", VixDiskLibSessionIdCreds),
      ("ticketId", c_void_p),       # internal use only
   ]


class VixDiskLibConnectParams(Structure):
   _fields_ = [
      ("vmxSpec", c_char_p),
      ("serverName", c_char_p),
      ("thumbPrint", c_char_p),
      ("privateUse", c_long),
      ("credType", c_int),
      ("creds", VixDiskLibCreds),
      ("port", c_uint),
      ("vimApiVer", c_char_p),
   ]


class VixDiskLibInfo(Structure):
   _fields_ = [
      ("biosGeo", VixDiskLibGeometry),
      ("physGeo", VixDiskLibGeometry),
      ("capacity", c_ulonglong),
      ("adapterType", c_int),
      ("numLinks", c_int),
      ("parentFileNameHint", c_char_p),
      ("uuid", c_char_p),
   ]

class VixDiskLibHandleStruct(Structure):
   pass

class VixDiskLibConnectParam(Structure):
   pass


VixDiskLibHandle = POINTER(VixDiskLibHandleStruct)
VixDiskLibConnection = POINTER(VixDiskLibConnectParam)
VixDiskLibProgressFunc = CFUNCTYPE(c_int, c_void_p, c_int)

VIXDISKLIB_FLAG_OPEN_UNBUFFERED  = 1 << 0 # // disable host disk caching
VIXDISKLIB_FLAG_OPEN_SINGLE_LINK = 1 << 1 # // don't open parent disk(s)
VIXDISKLIB_FLAG_OPEN_READ_ONLY   = 1 << 2 # // open read-only

# end types

_api = None

def GetApi():
   global _api
   if not _api:
      # XXX: Todo windows support
      try:
         _api = CDLL('vixDiskLibTest.dll')
      except:
         #
         _api = CDLL(os.path.abspath('libvixDiskLibTest.so'))
   return _api


LOGGERTYPE = CFUNCTYPE(None, c_char_p)
# Be explicit about function signatures
GetApi().VixDiskLibTest_InitEx.restype = c_ulonglong
GetApi().VixDiskLibTest_InitEx.argtypes = [c_uint, c_uint, LOGGERTYPE, LOGGERTYPE, LOGGERTYPE, c_char_p, c_char_p]
GetApi().VixDiskLibTest_Init.restype = c_ulonglong
GetApi().VixDiskLibTest_Init.argtypes = [c_uint, c_uint, LOGGERTYPE, LOGGERTYPE, LOGGERTYPE, c_char_p]
GetApi().VixDiskLib_SetConfigOption.restype = None
GetApi().VixDiskLib_SetConfigOption.argtypes = [c_int, c_void_p]
GetApi().VixDiskLib_SetInjectedFault.restype = c_uint16
GetApi().VixDiskLib_SetInjectedFault.argtypes = [c_int, c_uint16, c_int]
GetApi().VixDiskLib_Exit.restype = None
GetApi().VixDiskLib_Exit.argtypes = []
GetApi().VixDiskLib_ListTransportModes.restype = c_char_p
GetApi().VixDiskLib_ListTransportModes.argtypes = []
GetApi().VixDiskLib_Cleanup.restype = c_ulonglong
GetApi().VixDiskLib_Cleanup.argtypes = [POINTER(VixDiskLibConnectParams), c_uint_p, c_uint_p]
GetApi().VixDiskLib_Connect.restype = c_ulonglong
GetApi().VixDiskLib_Connect.argtypes = [POINTER(VixDiskLibConnectParams), POINTER(VixDiskLibConnection)]
GetApi().VixDiskLib_PrepareForAccess.restype = c_ulonglong
GetApi().VixDiskLib_PrepareForAccess.argtypes = [POINTER(VixDiskLibConnectParams), c_char_p]
GetApi().VixDiskLib_ConnectEx.restype = c_ulonglong
GetApi().VixDiskLib_ConnectEx.argtypes = [POINTER(VixDiskLibConnectParams), c_int,
                                          c_char_p, c_char_p,
                                          POINTER(VixDiskLibConnection)]
GetApi().VixDiskLib_Disconnect.restype = c_ulonglong
GetApi().VixDiskLib_Disconnect.argtypes = [VixDiskLibConnection]
GetApi().VixDiskLib_EndAccess.restype = c_ulonglong
GetApi().VixDiskLib_EndAccess.argtypes = [POINTER(VixDiskLibConnectParams), c_char_p]
GetApi().VixDiskLib_Create.restype = c_ulonglong
GetApi().VixDiskLib_Create.argtypes = [POINTER(VixDiskLibConnection), c_char_p,
                                       POINTER(VixDiskLibCreateParams),
                                       VixDiskLibProgressFunc, c_void_p]
GetApi().VixDiskLib_CreateChild.restype = c_ulonglong
GetApi().VixDiskLib_CreateChild.argtypes = [VixDiskLibHandle, c_char_p,
                                            c_int, # VixDiskLibDiskType
                                            VixDiskLibProgressFunc, c_void_p]
GetApi().VixDiskLib_Open.restype = c_ulonglong
GetApi().VixDiskLib_Open.argtypes = [VixDiskLibConnection, c_char_p, c_uint,
                                     POINTER(VixDiskLibHandle)]
GetApi().VixDiskLib_GetInfo.restype = c_ulonglong
GetApi().VixDiskLib_GetInfo.argtypes = [VixDiskLibHandle,
                                        POINTER(POINTER(VixDiskLibInfo))]
GetApi().VixDiskLib_FreeInfo.restype = None
GetApi().VixDiskLib_FreeInfo.argtypes = [POINTER(VixDiskLibInfo)]
GetApi().VixDiskLib_GetTransportMode.restype = c_char_p
GetApi().VixDiskLib_GetTransportMode.argtypes = [VixDiskLibHandle]
GetApi().VixDiskLib_Close.restype = c_ulonglong
GetApi().VixDiskLib_Close.argtypes = [VixDiskLibHandle]
GetApi().VixDiskLib_Read.restype = c_ulonglong
GetApi().VixDiskLib_Read.argtypes = [VixDiskLibHandle, c_ulonglong, c_ulonglong, c_char_p]
GetApi().VixDiskLib_Write.restype = c_ulonglong
GetApi().VixDiskLib_Write.argtypes = [VixDiskLibHandle, c_ulonglong, c_ulonglong, POINTER(c_ubyte)]
GetApi().VixDiskLib_ReadMetadata.restype = c_ulonglong
GetApi().VixDiskLib_ReadMetadata.argtypes = [VixDiskLibHandle, c_char_p, c_char_p, c_ulonglong, POINTER(c_ulonglong)]
GetApi().VixDiskLib_WriteMetadata.restype = c_ulonglong
GetApi().VixDiskLib_WriteMetadata.argtypes = [VixDiskLibHandle, c_char_p, c_char_p]
GetApi().VixDiskLib_GetMetadataKeys.restype = c_ulonglong
GetApi().VixDiskLib_GetMetadataKeys.argtypes = [VixDiskLibHandle, c_char_p, c_ulonglong, POINTER(c_ulonglong)]
GetApi().VixDiskLib_Unlink.restype = c_ulonglong
GetApi().VixDiskLib_Unlink.argtypes = [VixDiskLibConnection, c_char_p]
GetApi().VixDiskLib_Grow.restype = c_ulonglong
GetApi().VixDiskLib_Grow.argtypes = [VixDiskLibConnection, c_char_p, c_ulonglong, c_int,
                                     VixDiskLibProgressFunc, c_void_p]
GetApi().VixDiskLib_Shrink.restype = c_ulonglong
GetApi().VixDiskLib_Shrink.argtypes = [VixDiskLibHandle, VixDiskLibProgressFunc, c_void_p]
GetApi().VixDiskLib_Defragment.restype = c_ulonglong
GetApi().VixDiskLib_Defragment.argtypes = [VixDiskLibHandle, VixDiskLibProgressFunc, c_void_p]
GetApi().VixDiskLib_Rename.restype = c_ulonglong
GetApi().VixDiskLib_Rename.argtypes = [c_char_p, c_char_p]
GetApi().VixDiskLib_Clone.restype = c_ulonglong
GetApi().VixDiskLib_Clone.argtypes = [VixDiskLibConnection, c_char_p,
                                      VixDiskLibConnection, c_char_p,
                                      POINTER(VixDiskLibCreateParams),
                                      VixDiskLibProgressFunc, c_void_p, c_int]
GetApi().VixDiskLib_GetErrorText.restype = c_char_p
GetApi().VixDiskLib_GetErrorText.argtypes = [c_ulonglong, c_char_p]
GetApi().VixDiskLib_FreeErrorText.restype = None
GetApi().VixDiskLib_FreeErrorText.argtypes = [c_char_p]
GetApi().VixDiskLib_IsAttachPossible.restype = c_ulonglong
GetApi().VixDiskLib_IsAttachPossible.argtypes = [VixDiskLibHandle, VixDiskLibHandle]
GetApi().VixDiskLib_Attach.restype = c_ulonglong
GetApi().VixDiskLib_Attach.argtypes = [VixDiskLibHandle, VixDiskLibHandle]
GetApi().VixDiskLib_SpaceNeededForClone.restype = c_ulonglong
GetApi().VixDiskLib_SpaceNeededForClone.argtypes = [VixDiskLibHandle, c_uint, POINTER(c_ulonglong)]
GetApi().VixDiskLib_CheckRepair.restype = c_ulonglong
GetApi().VixDiskLib_CheckRepair.argtypes = [VixDiskLibConnection, c_char_p, c_int]
GetApi().VixDiskLib_GetConnectParams.restype = c_ulonglong
GetApi().VixDiskLib_GetConnectParams.argtypes = [VixDiskLibConnection, POINTER(POINTER(VixDiskLibConnectParams))]
GetApi().VixDiskLib_FreeConnectParams.restype = None
GetApi().VixDiskLib_FreeConnectParams.argtypes = [POINTER(VixDiskLibConnectParams)]


class VixDiskLibException(exceptions.Exception):
   def __init__(self, err, *args, **kwargs):
      self.err = err;
      super(Exception, self).__init__(*args, **kwargs)

   def Error(self):
      return self.err

   def ErrorText(self):
      res = GetApi().VixDiskLib_GetErrorText(self.err, None)
      result = res
      GetApi().VixDiskLib_FreeErrorText(res)
      return result

   def __str__(self):
      return super(Exception, self).__str__() + " (error %d)" % self.err


def InitEx(majorVersion, minorVersion, logCb, warnCb, panicCb, libDir, configFile):
   args = []
   for cb in (logCb, warnCb, panicCb):
      if cb:
         cb.handle = LOGGERTYPE(cb)
         args.append(cb.handle)
      else:
         args.append(None)
   res = GetApi().VixDiskLibTest_InitEx(majorVersion, minorVersion,
                                        args[0], args[1], args[2],
                                        libDir, configFile)
   if VIX_FAILED(res):
      raise VixDiskLibException(res, "Failed to call InitEx()")

def Init(majorVersion, minorVersion, logCb, warnCb, panicCb, libDir):
   args = []
   for cb in (logCb, warnCb, panicCb):
      if cb:
         cb.handle = LOGGERTYPE(cb)
         args.append(cb.handle)
      else:
         args.append(None)

   res = GetApi().VixDiskLibTest_Init(majorVersion, minorVersion,
                                      args[0], args[1], args[2],
                                      libDir)
   if VIX_FAILED(res):
      raise VixDiskLibException(res, "Failed to call Init()")

def Exit():
   GetApi().VixDiskLib_Exit()

def SetConfigOption(key, value):
   GetApi().VixDiskLib_SetConfigOption(key, c_void_p(value))

def SetInjectedFault(optionId, enabled, err):
   return GetApi().VixDiskLib_SetInjectedFault(optionId, enabled, err)

class VixDiskLib(object):
   def __init__(self):
      self._params = None
      self._connPtr = None

   @staticmethod
   def kwargsToVixDiskLibConnectParams(**kwargs):

      vmxSpec = kwargs.get("vmxSpec", None)
      server = kwargs.get("server", None)
      if not vmxSpec or not server:
         raise VixDiskLibException(VIX_E_FAIL, "Need at least a vmxSpec and server to connect")
      port = kwargs.get("port", 443)
      thumbPrint = kwargs.get("thumbPrint", None)
      user = kwargs.get("user", None)
      pswd = kwargs.get("password", None)
      cookie = kwargs.get("cookie", None)
      key = kwargs.get("key", None)
      ticket = kwargs.get("ticket", None)
      vimApiVer = kwargs.get("vimApiVer", None)
      params = VixDiskLibConnectParams()
      if cookie and user and key:
         params.creds.sessionId.userName = user
         params.creds.sessionId.key = key
         params.creds.sessionId.cookie = cookie
         params.credType = VIXDISKLIB_CRED_SESSIONID
      elif ticket:
         params.creds.ticketId = ticket
         params.credType = VIXDISKLIB_CRED_TICKETID
      elif user and pswd is not None:
         params.creds.uid.userName = user
         params.creds.uid.password = pswd
         params.credType = VIXDISKLIB_CRED_UID
      else:
         raise VixDiskLibException(VIX_E_FAIL, "No credentials specified!")
      params.vmxSpec = vmxSpec
      params.serverName = server
      params.port = port
      params.thumbPrint = thumbPrint
      params.vimApiVer = vimApiVer
      return params

   def ListTransportModes(self):
      res = GetApi().VixDiskLib_ListTransportModes()
      return res.split(':')

   def Connect(self, **kwargs):
      params = self.kwargsToVixDiskLibConnectParams(**kwargs)
      conn = VixDiskLibConnection()
      res = GetApi().VixDiskLib_Connect(pointer(params), byref(conn))
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Couldn't Connect")
      self._connPtr = conn
      self._params = params

   def PrepareForAccess(self, appId, **kwargs):
      params = self.kwargsToVixDiskLibConnectParams(**kwargs)
      res = GetApi().VixDiskLib_PrepareForAccess(byref(params), appId)
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Couldn't PrepareForAccess")

   def Cleanup(self, **kwargs):
      cleaned = c_uint()
      remaining = c_uint()
      params = self.kwargsToVixDiskLibConnectParams(**kwargs)
      res = GetApi().VixDiskLib_Cleanup(pointer(params), byref(cleaned), byref(remaining))
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Couldn't ConnectEx")
      return (cleaned.value, remaining.value)

   def ConnectEx(self, readOnly, ssRef, modes, **kwargs):
      params = self.kwargsToVixDiskLibConnectParams(**kwargs)
      if modes is not None and type(modes) == type([]):
            modes = ":".join(modes)
      conn = VixDiskLibConnection()
      res = GetApi().VixDiskLib_ConnectEx(pointer(params), readOnly, ssRef, modes, byref(conn))
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Couldn't ConnectEx")
      self._params = params
      self._connPtr = conn

   def Disconnect(self):
      res = GetApi().VixDiskLib_Disconnect(self._connPtr)
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Disconnect failed!")
      self._connPtr = None
      self._params = None

   def EndAccess(self, appId, **kwargs):
      params = self.kwargsToVixDiskLibConnectParams(**kwargs)
      res = GetApi().VixDiskLib_EndAccess(byref(params), appId)
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Couldn't EndAccess")

   def Create_local(self, path, diskType, adapterType, hwVersion, capacity,
              progressFunc, progressData):
      # a void connection
      conn = VixDiskLibConnection()

      params = VixDiskLibCreateParams()
      params.diskType = diskType
      params.adapterType = adapterType
      params.hwVersion = hwVersion
      params.capacity = capacity
      res = GetApi().VixDiskLib_Create(conn, path, byref(params),
                                       progressFunc, cast(progressData, c_void_p))
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Couldn't Create!")

   def Create(self, path, diskType, adapterType, hwVersion, capacity,
              progressFunc, progressData):
      params = VixDiskLibCreateParams()
      params.diskType = diskType
      params.adapterType = adapterType
      params.hwVersion = hwVersion
      params.capacity = capacity
      res = GetApi().VixDiskLib_Casdfasdfreate(None, path, byref(params),
                                       progressFunc, cast(progressData, c_void_p))
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Couldn't Create!")

   class VixDisk(object):
      def __init__(self, vixHandle):
         self._h = vixHandle

      def CreateChild(self, path, diskType, progressFunc, progressData):
         res = GetApi().VixDiskLib_CreateChild(self._h, path, diskType,
                                               progressFunc, cast(progressData, c_void_p))
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Couldn't CreateChild!")

      def GetInfo(self):
         info = POINTER(VixDiskLibInfo)()
         res = GetApi().VixDiskLib_GetInfo(self._h, pointer(info))
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Couldn't GetInfo")
         d = dict()
         for f in [ \
               "biosGeo", \
               "physGeo", \
               "capacity", \
               "adapterType", \
               "numLinks", \
               "parentFileNameHint", \
               "uuid"]:
             d[f] = getattr(info.contents, f)
         GetApi().VixDiskLib_FreeInfo(info)
         return d

      def GetTransportMode(self):
         res = GetApi().VixDiskLib_GetTransportMode(self._h)
         return res[:]

      def Close(self):
         res = GetApi().VixDiskLib_Close(self._h)
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Failed to Close()!")
         self._h = None

      def Read(self, startSector, count):
         buf = create_string_buffer(count*VIXDISKLIB_SECTOR_SIZE)
         res = GetApi().VixDiskLib_Read(self._h, startSector, count, buf)
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Failed to Read()!")
         #return buf.raw[:]                                  #to string
         return buf.raw
         #return buf

      def Write(self, startSector, data):
         l = len(data)
         assert l and l % VIXDISKLIB_SECTOR_SIZE == 0
         count = l/VIXDISKLIB_SECTOR_SIZE
         #raw_data = (c_ubyte * l).from_buffer_copy(data)
         res = GetApi().VixDiskLib_Write(self._h, startSector, count, data)
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Failed to Write()!")

      def Write2(self, startSector, data):
         l = len(data)
         assert l and l % VIXDISKLIB_SECTOR_SIZE == 0
         count = l / VIXDISKLIB_SECTOR_SIZE
         raw_data = (c_ubyte * l).from_buffer_copy(data)
         print '....'
         res = GetApi().VixDiskLib_Write(self._h, startSector, count, raw_data)
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Failed to Write()!")


      def ReadMetadata(self, key):
         keySize = 4096
         buf = create_string_buffer(keySize)
         requiredLen = c_ulong(0)
         res = GetApi().VixDiskLib_ReadMetadata(self._h, key, buf, keySize, byref(requiredLen))
         if res == VIX_E_BUFFER_TOOSMALL:
            keySize = requiredLen.value
            buf = create_string_buffer(keySize)
            res = GetApi().VixDiskLib_ReadMetadata(self._h, key, buf, keySize, byref(requiredLen))
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Failed to ReadMetadata()!")
         return buf.value

      def WriteMetadata(self, key, val):
         res = GetApi().VixDiskLib_WriteMetadata(self._h, key, val)
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Failed to WriteMetadata()!")

      def GetMetadataKeys(self):
         requiredLen = c_ulong()
         res = GetApi().VixDiskLib_GetMetadataKeys(self._h, None, 0, byref(requiredLen))
         buf = None
         keys = []
         if res == VIX_E_BUFFER_TOOSMALL and requiredLen.value > 0:
            buf = create_string_buffer(requiredLen.value)
            res = GetApi().VixDiskLib_GetMetadataKeys(self._h, buf, requiredLen, byref(requiredLen))
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Failed to GetMetadataKeys()!")
         if buf:
            buf = cast(buf, POINTER(c_char))
            start = 0
            x = 0
            while x < requiredLen.value - 1:
               if buf[x] == '\0':
                  if start != x:
                     keys.append(buf[start:x])
                  if buf[x+1] == '\0': # end of the result strings
                     break
                  start = x + 1
               x += 1
         return keys

      def Shrink(self, progressFunc, data):
         res = GetApi().VixDiskLib_Shrink(self._h, progressFunc, cast(data, c_void_p))
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Failed to Shrink!")

      def Defragment(self, progressFunc, data):
         res = GetApi().VixDiskLib_Defragment(self._h, progressFunc, cast(data, c_void_p))
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Failed to Defragment!")

      def IsAttachPossible(self, other):
         res = GetApi().VixDiskLib_IsAttachPossible(self._h, other._h)
         return VIX_SUCCEEDED(res)

      def Attach(self, child):
         res = GetApi().VixDiskLib_Attach(self._h, child._h)
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Failed to Attach!")

      def SpaceNeededForClone(self, newType):
         space = c_ulonglong(0)
         res = GetApi().VixDiskLib_SpaceNeededForClone(self._h, newType, byref(space))
         if VIX_FAILED(res):
            raise VixDiskLibException(res, "Failed to SpaceNeededForClone!")
         return space.value


   def Open(self, path, flags):
      h = VixDiskLibHandle()
      res = GetApi().VixDiskLib_Open(self._connPtr, path, flags, pointer(h))
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Couldn't open disk %s!" % path)
      return self.VixDisk(h)


   def open_local(self, path, flags):
      # a void connection to access local file
      conn = VixDiskLibConnection()
      params = VixDiskLibConnectParams()
      GetApi().VixDiskLib_Connect(pointer(params), byref(conn))
      h = VixDiskLibHandle()
      res = GetApi().VixDiskLib_Open(conn, path, flags, pointer(h))
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Couldn't open disk %s!" % path)
      return self.VixDisk(h)

   def Unlink(self, path):
      res = GetApi().VixDiskLib_Unlink(self._connPtr, path)
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Failed to Unlink!")

   def Grow(self, path, capacitySectors, updateGeo, progressFunc, progressData):
      res = GetApi().VixDiskLib_Grow(self._connPtr, path, capacitySectors, updateGeo,
                                     progressFunc, cast(progressData, c_void_p))
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Failed to Grow!")

   def Rename(self, src, dst):
      res = GetApi().VixDiskLib_Rename(src, dst)
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Failed to Rename!")

   def Clone(self, dstConn, dstPath, srcPath,
             diskType, adapterType, hwVersion, capacity,
             progressFunc, data, overWrite):
      params = VixDiskLibCreateParams()
      params.diskType = diskType
      params.adapterType = adapterType
      params.hwVersion = hwVersion
      params.capacity = capacity
      res = GetApi().VixDiskLib_Clone(dstConn, dstPath, self._connPtr, srcPath,
                                      byref(params), progressFunc, data, overWrite)

      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Failed to Clone!")

   def CheckRepair(self, filename, doRepair):
      res = GetApi().VixDiskLib_CheckRepair(self._connPtr, filename, doRepair)
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Failed to CheckRepair!")

   def GetConnectParams(self):
      params = POINTER(VixDiskLibConnectParams)()
      result = VixDiskLibConnectParams()
      res = GetApi().VixDiskLib_GetConnectParams(self._connPtr, byref(params))
      if VIX_FAILED(res):
         raise VixDiskLibException(res, "Failed to GetConnectParams!")
      result.vmxSpec = params.contents.vmxSpec
      result.serverName = params.contents.serverName
      result.thumbPrint = params.contents.thumbPrint
      result.creds = params.contents.creds
      result.port = params.contents.port
      GetApi().VixDiskLib_FreeConnectParams(params)
      return result


if __name__ == "__main__":
   GetApi()