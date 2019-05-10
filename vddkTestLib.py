###########################################################
# Copyright 2012-2015 VMware, Inc.  All rights reserved. -- VMware Confidential
###########################################################

from pyvddk import *
import os
import threading
import time
import shutil
import random
import sys
import tempfile
import unittest
import hashlib
import shutil
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect

from testConfig import GetConfig
# from pprint import pprint as PP

_Runners = {}

try:
   from multiprocessing import Pool
except ImportError:
   def Pool(count):
      class FakePool(object):
         def __init__(self, cnt):
            pass
         def map(self, func, args):
            return map(func, args)
      return FakePool(count)

# must be called before doing anyting with the test framework
def TestsInit():
   pass

def ComputeFileHash(fileName):
   """
   Return the SHA1 hash for a given file. We actually cache the SHA1 hash
   for the file on disk, so that we don't have to re-compute it every time.

   SHA1 hash recomputation will be triggered if there is on cached value or
   if the cache file's change time is older than the change time for the
   file whose hash it contains.

   @param fileName IN: Name of file for which to return the SHA1 hash.
   """

   # See if the sha1 hash for this file is already cached
   shaName = fileName + "-sha1"

   if not(os.path.isfile(shaName)) or (os.path.getctime(shaName) <= os.path.getctime(fileName)):
      # Compute hash if it does not yet exist or is out of date
      h = hashlib.sha1()
      f = file(fileName,"rb")
      blockSize = 65536
      block = f.read(blockSize)
      while block != "":
         h.update(block)
         block = f.read(blockSize)
      f.close()
      hash = h.hexdigest()

      # write hash
      f = file(shaName, "w")
      f.write(hash)
      f.close()

   else:
      # Hash already cached, read it in
      f = file(shaName, "r")
      hash = f.read()
      f.close()

   return hash

def RandomBlock(maxSize = 0):
   """
   Creates a generator object that yields a block of pseudo-random data from
   /dev/urandom each time next() is called

   @param maxSize IN: the maximum blocksize returned by this generator for
   each call to next()
   """

   if maxSize == 0:
      maxSize = GetMaxBlockSize()

   f = file('/dev/urandom', 'rb')
   while True:
      yield f.read(random.randint(0, maxSize))

def CreateScratchFile(outPath, size):
   """ Create a file full of random data and store it in outPath.
      @param outPath IN: the path to store the file at
      @param size IN: the size in MB of the file
   """
   blockSize = 1024**2
   size = size * blockSize
   f = file(outPath, "wb")

   src = file('/dev/urandom')
   offset = 0
   while offset < size:
      f.write(src.read(blockSize))
      offset += blockSize
   src.close()
   f.close()

def ScratchPath(dir, fname):
   """ Return the path we should use for the directory/filename combination
      @param dir IN: the directory to create the path from
      @param fname IN: the filename we should use

      @return the joined path
   """
   p = os.path.join(GetConfig().scratchPath, dir)
   if not os.path.isdir(p):
      os.makedirs(p)
   return os.path.join(p,fname)

def SetupScratchDir(scratchPath, files, sizes):
   """ create the list of files with the corresponding list of megabyte based
   sizes in directory scratchPath
   """
   scratchDir = os.path.join(GetConfig().scratchPath, scratchPath)
   if not os.path.isdir(scratchDir):
      os.makedirs(scratchDir)
   for f,sz in zip(files, sizes):
      fullPath = os.path.join(scratchDir, f)
      if not os.path.isfile(fullPath) or \
         os.path.getsize(fullPath) != sz * 1024**2:
         CreateScratchFile(fullPath, sz)
   return map(os.path.join, [scratchDir] * len(files), files)

def RunSequence(evt, jobs):
   """
   Run a sequence of functions specified in jobs
   @param evt IN: the event to set() on completion.  Can be None
   @param jobs IN: the two-item tuple containing (functionName, [args])
   """
   # print "RUN: %s" % str(jobs)
   for j in jobs:
      # print "---Job: %s" % str(j)
      j[0](*j[1])
   if evt:
      evt.set()

class ThreadWithResult(threading.Thread):
   """
   The python threading library does not allow for threads to return an exit
   code to whoever spawned them. We use this class to work around this:

   If the worker function encounters an error, we have it throw a
   VixDiskLibException, which our ThreadWithResult class catches and stores
   in a data member, that can be queried after a "join" for the thread.
   """
   def run(self):
      try:
         threading.Thread.run(self)
      except VixDiskLibException, e:
         self.result = e.Error()
         self.errMsg = str(e)
      else:
         self.result = 0

def ThreadSequence(jobs):
   """
   create a thread object that will run the sequence specified in jobs
   @param jobs IN: the dict with a single key mapping jobname to jobsequence
   """
   global _Runners
   evt = None
   name, jobs = jobs
   evt = threading.Event()
   _Runners[name] = evt
   return ThreadWithResult(target=RunSequence, args = [evt, jobs])

def WaitFor(store, namedSequence):
   """
   Wait for a named sequence to complete

   @param namedSequence the sequence to wait for
   """
   # print "WAITING FOR %s" % namedSequence
   global _Runners
   evt = _Runners.get(namedSequence, None)
   if evt:
      evt.wait()
      _Runners[namedSequence] = None

def RunThreads(store, th):
   """
   Run each item in a dict as a separate thread

   @param store IN: the store to run jobs for
   @param th IN: the threads dict containing mappings of job name to job
   sequence
   """

   result = 0
   thObjs = map(ThreadSequence, [store] * len(th), th.items())
   for thr in thObjs:
      thr.start()
   for thr in thObjs:
      thr.join()
      if thr.result != 0:
         print thr.errMsg
         result = thr.result
   return result

def Progress(id, msg):
   """
   print a progress msg (for use in a sequence)

   @param id IN: something to id this progress msg
   @param msg IN: the msg to print
   """
   print "TEST(%s) => %s" % (id, msg)
   sys.stdout.flush()
   return True  # for use in lambda

# a unittest base class useful for test cases to inherit from
class VddkTestCase(unittest.TestCase):
   def run(self, result=None):
      if GetConfig().stopOnFailure and (result.failures or result.errors):
         print "aborted due to previous failure"
      else:
         super(VddkTestCase, self).run(result)

   def InitLib(self):
      TestsInit()

   def setUp(self):
      """
      setup the test case
      """
      self.InitLib()
      self._path = None
      self._config = GetConfig()
      # SetLogLevel(self._config.logLevel)
      self.r = RandomBlock()

   def tearDown(self):
      """
      tear down the test case
      """
      pass


def WaitForTasks(tasks, si):
   """
   Given the service instance si and tasks, it returns after all the
   tasks are complete
   """

   pc = si.content.propertyCollector

   taskList = [str(task) for task in tasks]

   # Create filter
   objSpecs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                                                            for task in tasks]
   propSpec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                         pathSet=[], all=True)
   filterSpec = vmodl.query.PropertyCollector.FilterSpec()
   filterSpec.objectSet = objSpecs
   filterSpec.propSet = [propSpec]
   filter = pc.CreateFilter(filterSpec, True)

   try:
      version, state = None, None

      # Loop looking for updates till the state moves to a completed state.
      while len(taskList):
         update = pc.WaitForUpdates(version)
         for filterSet in update.filterSet:
            for objSet in filterSet.objectSet:
               task = objSet.obj
               for change in objSet.changeSet:
                  if change.name == 'info':
                     state = change.val.state
                  elif change.name == 'info.state':
                     state = change.val
                  else:
                     continue

                  if not str(task) in taskList:
                     continue

                  if state == vim.TaskInfo.State.success:
                     # Remove task from taskList
                     taskList.remove(str(task))
                  elif state == vim.TaskInfo.State.error:
                     raise task.info.error
         # Move to next version
         version = update.version
   finally:
      if filter:
         filter.Destroy()

def DCFromHost(host, user, pswd, thumbprint=None):
   si = SmartConnect(host = host, user = user, pwd = pswd, port = 443, thumbprint = thumbprint)
   if not si:
      raise VimException("Couldn't connect to host")
   dc = si.RetrieveContent().rootFolder.childEntity[0]
   return (si, dc)

def FindVm(dc, vmName):
   vmFolder = dc.vmFolder
   def getVms(fldr):
      for obj in fldr.childEntity:
         if isinstance(obj, vim.VirtualMachine):
            vm = obj
            if hasattr(vm, 'summary') and vm.summary.config.name == vmName:
               return vm
         else:
            vm = getVms(obj)
            if vm:
               return vm
      return None
   return getVms(vmFolder)

def CreateLinkedClone(si, dc, src, dst):
   vmSrc = FindVm(dc, src)
   task = vmSrc.CreateSnapshot("test-snap-clone", "linked clone snapshot", False, True)
   WaitForTasks([task], si)
   relSpec = vim.vm.RelocateSpec()
   relSpec.diskMoveType = vim.vm.RelocateSpec.DiskMoveOptions.createNewChildDiskBacking
   cloneSpec = vim.vm.CloneSpec()
   cloneSpec.powerOn = False
   cloneSpec.template = False
   cloneSpec.location = relSpec
   cloneSpec.snapshot = vmSrc.snapshot.currentSnapshot
   print "Creating clone...",
   task  = vmSrc.Clone(vmSrc.parent, dst, cloneSpec)
   WaitForTasks([task], si)
