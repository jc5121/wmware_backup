###########################################################
# Copyright 2012-2015 VMware, Inc.  All rights reserved. -- VMware Confidential
###########################################################
from os.path import abspath

class TestConfig(object):
   def __init__(self):
      self.logLevel = 0
      self.list = False
      self.testsDir = "."
      self.tests = []
      self.libDir = None
      self.creds = {}

   def Dump(self):
      print "logLevel: %d\ntestDir: %s\nlibDir: %s" % \
      (self.logLevel, abspath(self.testDir), abspath(self.libDir))

_config = None

def SetConfig(config):
   global _config
   _config = config

def GetConfig():
   global _config
   return _config

def TestsFromConfig(suiteName, config, testObjList, testMap):
   '''
      suiteName -> name of this suite
      config -> unitdriver config object
      testObjList -> list of test name strings
      testMap -> dict mapping test names in testObjList to TestCase objects
   '''
   wantTests = config.tests
   if not wantTests:
      # if none, then give us all the tests
      wantTests = testObjList
   elif wantTests[0] == suiteName:
      wantTests = testObjList
   a = [testMap[test] for test in wantTests if testMap.has_key(test)]
   return a
