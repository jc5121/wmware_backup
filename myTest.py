###########################################################
# Copyright 2012-2015 VMware, Inc.  All rights reserved. -- VMware Confidential
###########################################################

from vddkTestLib import *
from testConfig import GetConfig


####
# A helper class for the quick and dirty drafting of a test, while still being
# able to use all the nifty testing framework we have in our Python test
# suite.  Just edit the "MyCase function to your liking.
####
class MyTest(VddkTestCase):
    def __init__(self, storeName):
        self._config = GetConfig()
        SetLogLevel(self._config.logLevel)

    #####
    # Custom test, edit to please (but don't check in)
    #####
    def MyCase(self):
        return 0
