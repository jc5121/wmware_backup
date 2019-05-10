###########################################################
# Copyright 2012-2015 VMware, Inc.  All rights reserved. -- VMware Confidential
###########################################################
import unittest
import optparse
import glob
from testConfig import *
import types
import sys
import os


_allTests = []

def GetAllTests():
   global _allTests
   return _allTests

def OptionsParser():
   usage = "Usage: %prog [options] <tests to run> -- if ommitted, all tests are run.\nCan also be a suite name"
   parser = optparse.OptionParser(usage=usage)
   parser.add_option("-L", "--loglevel", dest="logLevel", type="int",
                     default=0,
                     help="turn up the logging level (0-7)")
   parser.add_option("-l", "--list", dest="list", action="store_true",
                     default=False,
                     help="list the available tests to run")
   parser.add_option("-d", "--directory", dest="testDir", type="string",
                     default=".",
                     help="directory to look for tests")
   parser.add_option("-s", "--start-with", dest="startTest",
                     default=None,
                     help="start the test run with this test")
   parser.add_option("-a", "--abort-on-fail", dest="stopOnFailure",
                     action="store_true", default=False,
                     help="Don't run any further tests if one fails")
   parser.add_option("-x", "--libdir", dest="libDir", type="string",
                     default=".", help="vddk library directory")
   parser.add_option("--my-test", dest="runMyTest",
                     action="store_true", default=False,
                     help="Run my own custom test in myTest.py, do not invoke framework")
   opts,args = parser.parse_args()
   config = TestConfig()
   config.logLevel = opts.logLevel
   config.list = opts.list
   config.testDir = opts.testDir
   config.tests = args or []
   config.startTest = opts.startTest
   config.stopOnFailure = opts.stopOnFailure
   config.runMyTest = opts.runMyTest
   config.libDir = opts.libDir

   try:
      import hostConfig
      hostConfig.UpdateConfig(config)
   except ImportError:
      pass
   config.Dump()
   SetConfig(config)
   return args

def ListTests():
   for t in GetAllTests():
      print t.shortDescription()

def DiscoverTests(testDir):
   global _allTests
   # find all python files in test directory
   fnames = [os.path.basename(f.replace('.py','')) for f in glob.glob('%s/*.py' % testDir)]
   fnames.sort()

   # imports require a module name only, so alter our path to include testDir
   sys.path.insert(0, testDir)

   #...and import them
   mods = dict([(m,__import__(m)) for m in fnames])
   for module in fnames:
      all = dir(mods[module])
      for f in all:
         g = getattr(mods[module], f)
         if type(g) == types.TypeType and \
            issubclass(g, VddkTestCase) and g.__name__ != 'VddkTestCase':
               for meth in dir(g):
                  if meth.startswith('test'):
                     obj = g(meth)
                     if hasattr(obj, 'isForked'):
                        # forked tests have to go first due to vmacore's not
                        # playing nicely with fork
                        _allTests.insert(0, obj)
                     else:
                        _allTests.append(obj)

def FilterTests(wantList, startTest=None):
   def itemTest(item):
      if wantList is None or \
         len(wantList) == 0 or \
         item.shortDescription().startswith(wantList[0]) or \
         item.shortDescription() in wantList:
         return True
      return False
   tests = filter(itemTest, GetAllTests())
   if startTest != None:
      for i in range(len(tests)):
         if tests[i].shortDescription() == startTest:
            tests = tests[i:]
            break
   return tests


def RunSuite(config):
   suite = FilterTests(config.tests, config.startTest)
   if not len(suite):
      print "No tests specified!"
      raise SystemExit
   unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suite))

def Refork():
   tcPython = "/build/toolchain/lin64/python-2.7.1/bin/python"
   numArgs = len(sys.argv[1:])
   for i in range(numArgs):
      if sys.argv[i] in ["-x", "--libdir"] and i < numArgs:
         print "GOT IT"
         ldPath = sys.argv[i+1]
         try:
            curEnv = os.environ["LD_LIBRARY_PATH"].split(':') or []
         except KeyError:
            curEnv = []
         print "CUR: %s " %curEnv
         if ldPath not in curEnv:
            curEnv.append(ldPath)
            print ldPath
         else:
            return
         os.environ["LD_LIBRARY_PATH"] = ":".join(curEnv)
         p = [tcPython, 'unitdriver.py'] + sys.argv[1:]
         os.execv(tcPython, p)

if __name__ == "__main__":
   Refork()
   args = OptionsParser()
   config = GetConfig()
   from vddkTestLib import VddkTestCase
   from myTest import *
   if config.runMyTest:
      test = MyTest(config.basePath)
      res = test.MyCase()
      if res == 0:
         print "OK\n"
      else:
         print "FAIL\n"
   else:
      DiscoverTests(config.testDir)
      if config.list:
         ListTests()
         raise SystemExit
      else:
         RunSuite(config)
