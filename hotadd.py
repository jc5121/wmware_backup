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

class HotaddCase(VddkTestCase):
   ###
   # Opens a disk link that is part of a backing hierarchy
   ###
   def testOpenDisk(self):
      """ hotadd/OpenDiskParent """
      DoInit()
      creds = GetConfig().creds["wdcEsx"]
      h,u,p = creds["hostname"], creds["username"], creds["password"]
      si, dc = DCFromHost(h,u,p)
      vm = FindVm(dc, "backupTarget")
      vmxSpec = "moref=%s" % str(vm).split(":")[1].strip("'")
      def killSnaps():
         try:
            snap = vm.snapshot.currentSnapshot
            while snap != None:
               task = snap.Remove(True, True)
               WaitForTasks([task], si)
               snap = vm.snapshot.currentSnapshot
         except AttributeError:
            pass
      #killSnaps()
      vix = VixDiskLib()
      vix.Cleanup(server = h,
                  vmxSpec = vmxSpec,
                  user = u,
                  password = p)
      task = vm.CreateSnapshot("backupTarget-snapshot", "xxx", False, True)
      WaitForTasks([task], si)
      backing = None
      last = None
      for d in vm.snapshot.currentSnapshot.config.hardware.device:
         if "vim.vm.device.VirtualDisk" in str(d):
            backing = d.backing
            break
      print "NAMES:"
      target = None
      while backing != None:
         print "====> %s" % backing.fileName
         last = target
         target = backing.fileName
         backing = backing.parent
      snap = vm.snapshot.currentSnapshot
      vix.ConnectEx(True, str(snap).split(":")[1].strip("'"), ["hotadd"],
                    server = h,
                    vmxSpec = vmxSpec,
                    user = u,
                    password = p)
      # this is the basemost disk
      for t in [target, last]:
         print "XXX: Opening disk %s" % t
         disk = vix.Open(t, VIXDISKLIB_FLAG_OPEN_READ_ONLY)
         data = disk.Read(0, 1)
         disk.Close()
      vix.Disconnect()
      vix.Cleanup(server = h,
                  vmxSpec = vmxSpec,
                  user = u,
                  password = p)
      snap.Remove(True, True)
      self.assert_(len(data) == 512)

   ### requires VC
   ### creates a linked clone and destroys it
   def XXXDisabled_testOpenLinkedCloneParent(self):
      """ hotadd/CreateLinkedAndOpen """
      DoInit()
      creds = GetConfig().creds["vadpHostEsx"]
      h,u,p = creds["hostname"], creds["username"], creds["password"]
      si, dc = DCFromHost(h,u,p)
      CreateLinkedClone(si, dc, "basicSuiteOpenDisk", "basicSuiteOpenDisk-clone")
      vm = FindVM(dc, "basicSuiteOpenDisk-clone")
      vm.Destroy()


if __name__ == "__main__":
    DoInit()