###################################################
# Copyright 2012-2015 VMware, Inc.  All rights reserved. -- VMware Confidential
###################################################

from pyvddk import *
import exceptions
import os

def Logger(msg):
   print "[LOG] %s" % msg,
def Panicker(msg):
   print "[PANIC] %s" % msg,
def Warner(msg):
   print "[WARN] %s" % msg,

def TestLog(msg):
   print "[TESTLOG] %s" % msg

def DoInit(libDir):
   InitEx(6,0, Logger, Warner, Panicker, libDir, None)


def initTests(libDir):
   DoInit(libDir)
   Exit()
   return 0

suiteMap = {
   'initTests' : initTests,
}

if __name__ == "__main__":
   import sys
   err = "No error"
   path = os.path.realpath(__file__)
   runDir = os.path.dirname(path)
   libDir = os.path.join(runDir, 'vmware-vix-disklib-distrib')
   def Go():
      try:
         suite = sys.argv[1]
         return suiteMap[suite](libDir)
      except IndexError:
         err = "No Suite specified!"
      except KeyError:
         err = "invalid suite specified!"
      TestLog(err)
      return 1
   sys.exit(Go())
