#!/usr/env python
# -*- coding: UTF-8 -*-

# Author: jchao

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import atexit
import getpass
import argparse
import sys
from vmware_cbt_tool import create_vm_snapshot, remove_vm_snapshot, get_dcftree, get_vm_list
from snapshot_operations import revert_vm_snapshot, list_snapshots_recursively, \
    get_snapshots_by_name_recursively, get_vm_config, power_off, power_on, revert
from cost_test import time_cost, space_cost
from backup import full_backup, full_restore, incremental_backup, incremental_restore, update_changeID


def GetArgs():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(
        description='Process args for create/remove/revert snapshot ')
    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='Remote host to connect to')
    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')
    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('-d', '--datacenter',
                        required=True,
                        action='store',
                        help='DataCenter Name')
    parser.add_argument('-f', '--folder',
                        required=False,
                        action='store',
                        help='Folder Name (must start with /, use / for root folder')
    parser.add_argument('-v', '--vmname',
                        required=False,
                        action='append',
                        help='Names of the Virtual Machines')
    parser.add_argument('--vm-uuid',
                        required=False,
                        action='append',
                        help='Instance UUIDs of the Virtual Machines')
    parser.add_argument('--create',
                        action='store_true',
                        default=False,
                        help='create snapshot')
    parser.add_argument('--remove',
                        action='store_true',
                        default=False,
                        help='remove snapshot')
    parser.add_argument('--revert',
                        action='store_true',
                        default=False,
                        help='revert from a snapshot')
    parser.add_argument('--snapshot_info',
                        action='store_true',
                        default=False,
                        help='Show snapshots info'
                        )
    parser.add_argument('--current_snapshot',
                        action='store_true',
                        default=False,
                        help='Show current snapshot info'
                        )
    parser.add_argument('--vm_config',
                        action='store_true',
                        default=False,
                        help='get the vm config info to file'
                        )
    parser.add_argument('--power_off',
                        action='store_true',
                        default=False,
                        help='power_off the vm'
                        )
    parser.add_argument('--power_on',
                        action='store_true',
                        default=False,
                        help='power_on the vm'
                        )
    parser.add_argument('--time_cost',
                        action='store_true',
                        default=False,
                        help='time cost test, write to a file'
                        )
    parser.add_argument('--space_cost',
                        action='store_true',
                        default=False,
                        help='space cost test, write to a file'
                        )
    parser.add_argument('--changeID',
                        action='store_true',
                        default=False,
                        help='get the changeID'
                        )
    parser.add_argument('--full_backup',
                        action='store_true',
                        default=False,
                        help='do full backup'
                        )
    parser.add_argument('--full_restore',
                        action='store_true',
                        default=False,
                        help='do full restore'
                        )
    parser.add_argument('--incremental_backup',
                        action='store_true',
                        default=False,
                        help='do incremental backup'
                        )
    parser.add_argument('--incremental_restore',
                        action='store_true',
                        default=False,
                        help='do incremental restore'
                        )
    args = parser.parse_args()

    if [args.create, args.remove, args.revert, args.snapshot_info, args.current_snapshot, args.vm_config,
        args.power_off, args.power_on, args.time_cost, args.space_cost, args.changeID, args.incremental_backup,
        args.full_backup, args.full_restore, args.incremental_restore].count(True) > 1:
        parser.error("Only one of --create, --remove, --revert, --snapshot_info, --current_snapshot, "
                     "--vm_config, --power_off, --power_on, --time_cost, --space_cost, --changeID, "
                     "--incremental_backup,--full_backup, --full_restore, --incremental_restore"
                     "allowed")

    if args.folder and not args.folder.startswith('/'):
        parser.error("Folder name must start with /")

    return args


def main():
    args = GetArgs()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
            (args.host, args.user))

    try:
        # get service_instance
        si = None
        try:
            si = SmartConnect(host=args.host,
                              user=args.user,
                              pwd=password,
                              port=int(args.port))
        except IOError as e:
            pass
        if not si:
            print ("Cannot connect to specified host using specified"
                   "username and password")
            sys.exit()

        atexit.register(Disconnect, si)

        content = si.content


        dcftree = {}
        dcView = content.viewManager.CreateContainerView(content.rootFolder,
                                                         [vim.Datacenter],
                                                         False)
        dcList = dcView.view
        dcView.Destroy()
        for dc in dcList:
            if dc.name == args.datacenter:
                dcftree[dc.name] = {}
                folder = ''
                get_dcftree(dcftree[dc.name], folder, dc.vmFolder)


        vm = None

        for vm in get_vm_list(args, dcftree):

            if args.create:
                print "INFO: VM %s trying to create snapshot now" % (vm.name)
                create_vm_snapshot(si, vm)
            if args.remove:
                print "INFO: VM %s trying to remove latest snapshot now" % (vm.name)
                # remove currentSnapshot
                remove_vm_snapshot(si, vm.snapshot.currentSnapshot)
            if args.revert:
                print "INFO: VM %s trying to revert now" % (vm.name)
                revert(si, vm)
            if args.snapshot_info:
                snapshot_list = list_snapshots_recursively(vm.snapshot.rootSnapshotList)
                for snapshot in snapshot_list:
                    print snapshot
                    #print type(snapshot)
            if args.current_snapshot:
                print type(vm.snapshot.currentSnapshot)
            if args.vm_config:
                get_vm_config(vm)
            if args.power_off:
                power_off(si, vm)
            if args.power_on:
                power_on(si, vm)
            if args.time_cost:
                time_cost(si, vm)
            if args.space_cost:
                space_cost(si, vm)
            if args.changeID:
                update_changeID(vm)
            if args.full_backup:
                full_backup(vm)
            if args.incremental_backup:
                incremental_backup(vm)
            if args.full_restore:
                full_restore(vm)
            if args.incremental_restore:
                incremental_restore(vm)

    except vmodl.MethodFault as e:
        print "Caught vmodl fault : " + e.msg
    except Exception as e:
        print "Caught unexpected Exception : " + str(e)
        raise


# start program
if __name__ == '__main__':
    main()