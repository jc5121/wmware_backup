###################################################
# Copyright 2012-2015 VMware, Inc.  All rights reserved. -- VMware Confidential
###################################################

from vddkTestLib import *
import exceptions

class VimException(exceptions.Exception):
   pass

def Logger(msg):
   print "[LOG] %s" % msg,
def Panicker(msg):
   print "[PANIC] %s" % msg,
def Warner(msg):
   print "[WARN] %s" % msg,

def DoInit():
   InitEx(5,0, Logger, Warner, Panicker, GetConfig().libDir, None)

class BasicCase(VddkTestCase):
   def testHello(self):
      """ basicSuite/TestHello """
      print "HELLO TEST SUITE!"
      def go(msg):
         print msg,
      InitEx(5,0, go, go, go, GetConfig().libDir, None)

   ###
   # Opens a disk link that is part of a backing hierarchy
   ###
   def testOpenDisk(self):
      """ basicSuite/OpenDiskParent """
      DoInit()
      creds = GetConfig().creds["vadpHostEsx"]
      h,u,p = creds["hostname"], creds["username"], creds["password"]
      si, dc = DCFromHost(h,u,p)
      vm = FindVm(dc, "basicSuiteOpenDisk")
      task = vm.CreateSnapshot("basicSuiteOpenDisk", "xxx", False, True)
      WaitForTasks([task], si)
      backing = None
      for d in vm.snapshot.currentSnapshot.config.hardware.device:
         if "vim.vm.device.VirtualDisk" in str(d):
            backing = d.backing
            break
      print "NAMES:"
      while backing != None:
         print "====> %s" % backing.fileName
         backing = backing.parent
      snap = vm.snapshot.currentSnapshot
      vix = VixDiskLib()
      vmxSpec = "moref=%s" % str(vm).split(":")[1].strip("'")
      vix.ConnectEx(False, str(snap).split(":")[1], ["nbd"],
                    server = h,
                    vmxSpec = vmxSpec,
                    user = u,
                    password = p)

      # this is the basemost disk
      disk = vix.Open("[datastore1]basicSuiteOpenDisk/disk-1000-0.vmdk", VIXDISKLIB_FLAG_OPEN_READ_ONLY)
      data = disk.Read(0, 1)
      disk.Close()
      snap.Remove(True, True)
      self.assert_(len(data) == 512)

   ### requires VC
   ### creates a linked clone and destroys it
   def XXXDisabled_testOpenLinkedCloneParent(self):
      """ basicSuite/CreateLinkedAndOpen """
      DoInit()
      creds = GetConfig().creds["vadpHostEsx"]
      h,u,p = creds["hostname"], creds["username"], creds["password"]
      si, dc = DCFromHost(h,u,p)
      CreateLinkedClone(si, dc, "basicSuiteOpenDisk", "basicSuiteOpenDisk-clone")
      vm = FindVM(dc, "basicSuiteOpenDisk-clone")
      vm.Destroy()
