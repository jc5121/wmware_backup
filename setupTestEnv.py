#!/usr/bin/env python

import os
import sys
import exceptions

class SetupException(exceptions.Exception):
   pass


_config = None

def GetConfig():
   global _config
   if not _config:
      _config = dict()
   return _config

# make symlinks
def GetVmTree():
   """
   return the fullpath to vddk build tree.  First looks at VMTREE, if empty,
   checks the first argument to the script
   """
   tree = os.environ.get('VMTREE', None)
   if not tree:
      tree = len(sys.argv) > 1 and sys.argv[1] or None
   if not tree:
      raise SetupException("Failed to find $VMTREE!")
   return os.path.abspath(tree)

def GetBuildType():
   return os.environ.get('VMBLD', 'obj')

def BuildSymlinks():
   tree = GetVmTree()
   bt = GetBuildType()
   join = os.path.join
   dir32 = join(tree, "build/%s" % bt)
   dir64 = join(tree, "build/%s-x64" % bt)
   glib = '/build/toolchain/lin64/glib-2.28.1/lib'
   ssl = '/build/toolchain/lin64/openssl-0.9.8x/lib'
   sslDiskLib = '/build/toolchain/lin64/openssl-1.0.0g/lib'
   pyFiles = "basicSuite.py  myTest.py  pyvddk.py  testConfig.py unitdriver.py  vddkTestLib.py hostConfig.py".split()
   pyFiles = [(join(tree, "apps/vixDiskLib/tests", x), "64/%s" % x) for x in pyFiles]

   pyvim = [
      (join(tree, "build/esx/obj/pyvmomi-00000/pyVmomi"), "64/pyVmomi"),
      (join(tree, "build/esx/obj/pyvim-00000/pyVim"), "64/pyVim"),
   ]


   toolchain = [
      (join(glib, "libglib-2.0.so.0.2800.1"), "64/libglib-2.0.so.0"),
      (join(glib, "libgmodule-2.0.so.0.2800.1"), "64/libgmodule-2.0.so.0"),
      (join(glib, "libgobject-2.0.so.0.2800.1"), "64/libgobject-2.0.so.0"),
      (join(glib, "libgthread-2.0.so.0.2800.1"), "64/libgthread-2.0.so.0"),
      (join(ssl, "libssl.so.0.9.8"), "64/libssl.so.0.9.8"),
      (join(ssl, "libcrypto.so.0.9.8"), "64/libcrypto.so.0.9.8"),
      (join(sslDiskLib, "libssl.so.1.0.0"), "64/libssl.so.1.0.0"),
      (join(sslDiskLib, "libcrypto.so.1.0.0"), "64/libcrypto.so.1.0.0"),
      ('/build/toolchain/lin64/curl-7.24.0/lib/libcurl.so.4.2.0', "64/libcurl.so.4"),

   ]
   maps = [
      (join(dir64, "apps/vixDiskLib/libvixDiskLib.so"), "64/libvixDiskLib.so"),
      (join(dir64, "apps/vixDiskLib/libvixDiskLib.so"), "64/libvixDiskLib.so.5"),
      (join(dir64, "apps/vixDiskLibTest/libvixDiskLibTest.so"), "64/libvixDiskLibTest.so"),
      (join(dir64, "apps/diskLibPlugin/libdiskLibPlugin.so"), "64/lib64/libdiskLibPlugin.so"),
      (join(dir64, "apps/vixDiskLibVim/libvixDiskLibVim.so"), "64/libvixDiskLibVim.so"),
      (join(dir64, "apps/vixDiskLibVim/libvixDiskLibVim.so"), "64/libvixDiskLibVim.so"),
      (join(dir64, "apps/vixMntapi/libvixMntapi.so"), "64/libvixMntapi.so"),
      (join(dir64, "vddk/vim/hostd/types/libtypes.so"), "64/libtypes.so"),
      (join(dir64, "vddk/vim/lib/vmacore/libvmacore.so"), "64/libvmacore.so"),
      (join(dir64, "vddk/vim/lib/vmomi/libvmomi.so"), "64/libvmomi.so"),
      (join(dir64, "vddk/gvmomi/libgvmomi.so"), "64/libgvmomi.so.0"),
   ]
   if not os.path.isdir("64"):
      os.mkdir("64")
   if not os.path.isdir("64/lib64"):
      os.mkdir("64/lib64")
   for s,t in toolchain + maps + pyFiles + pyvim:
      if not os.path.exists(t):
         os.symlink(s, t)

BuildSymlinks()
# /dbc/pa-dbc1010/dbarry/git/vmkernel-main/bora/build/obj-x64/apps/vixDiskLib/libvixDiskLib.so

# // deploy nimbus vm
### TODO

# // create json file / use env variables
### TODO create configuration writer (serialized json), have test framework
#  use it
