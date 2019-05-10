#!/usr/env python
# -*- coding: UTF-8 -*-

# Author: jchao

import sys
from pyVmomi import vim, vmodl
from vmware_cbt_tool import WaitForTasks


def revert(si, vm):
    """
    revert to current snapshot
    """
    revert_snap_task = None
    try:
        revert_snap_task = vm.snapshot.currentSnapshot.RevertToSnapshot_Task(suppressPowerOn=True)
    except vmodl.MethodFault as e:
        print "Failed to revert snapshot %s" % (e.msg)
        return False

    WaitForTasks([revert_snap_task], si)
    print "Success to revert snapshot"
    return True


def revert_vm_snapshot(si, snapshot):
    """
     revert a given snapshot
     """
    revert_snap_task = None
    try:
        revert_snap_task = snapshot.RevertToSnapshot_Task(suppressPowerOn=True)
    except vmodl.MethodFault as e:
        print "Failed to revert snapshot %s" % (e.msg)
        return False

    WaitForTasks([revert_snap_task], si)
    print "Success to revert snapshot"
    return True


def list_snapshots_recursively(snapshots):
    snapshot_data = []
    snap_text = ""
    for snapshot in snapshots:
        '''
        snap_text = "Name: %s; Description: %s; CreateTime: %s; State: %s" % (
                                        snapshot.name, snapshot.description,
                                        snapshot.createTime, snapshot.state)
        '''
        snapshot_data.append(snapshot)
        snapshot_data = snapshot_data + list_snapshots_recursively(
                                        snapshot.childSnapshotList)
    return snapshot_data


def get_snapshots_by_name_recursively(snapshots, snapname):
    snap_obj = []
    for snapshot in snapshots:
        if snapshot.name == snapname:
            snap_obj.append(snapshot)
        else:
            snap_obj = snap_obj + get_snapshots_by_name_recursively(
                                    snapshot.childSnapshotList, snapname)
    return snap_obj


# virtual machine configuration information ( vim.vm.ConfigInfo).
def get_vm_config(vm):
    filename = vm.name + '.config'
    config_file = open(filename, 'w')
    config_file.write(str(vm.config))
    config_file.close()
    # print type(vm.config)


def power_off(si, vm):
    """
     power_off a vm
     """
    power_off_task = None
    try:
        power_off_task = vm.PowerOff()
    except vmodl.MethodFault as e:
        print "Failed to power off %s" % (e.msg)
        return False

    WaitForTasks([power_off_task], si)
    print "Success to power_off "
    return True


def power_on(si, vm):
    """
     power_on a vm
     """
    power_on_task = None
    try:
        power_on_task = vm.PowerOn()
    except vmodl.MethodFault as e:
        print "Failed to power on %s" % (e.msg)
        return False

    WaitForTasks([power_on_task], si)
    print "Success to power on "
    return True



