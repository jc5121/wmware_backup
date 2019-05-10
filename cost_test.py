# /usr/evn/python
# -*- coding: UTF-8 -*-

# Author: jchao

from vmware_cbt_tool import create_and_remove_snapshot, create_vm_snapshot, remove_vm_snapshot

import time
import re


def time_cost(si, vm):
    filename = 'time_cost.log'
    cost_file = open(filename, 'a')

    total = 0
    i = 0

    # for capture ctrl+C and ensure to close the file
    try:
        while True:
            start = time.time()
            create_and_remove_snapshot(si, vm)
            end = time.time()
            total += end - start
            i += 1
            average = total / i
            cost_file.write(str(i) + ' ' + ' total: ' + str(total) + ' average: ' + str(average) + '\n')
            time.sleep(10)
    except KeyboardInterrupt:
        cost_file.close()


def space_cost(si, vm):
    filename = 'space_cost.log'
    # cost_file = open(filename, 'a')

    total = 0
    i = 0

    disk_list = vm.layout.snapshot
    for file_info in disk_list:
        print file_info
    # get_snapshot_size(vm)
    '''
    try:
        while True:
            create_vm_snapshot(si, vm)
            
            remove_vm_snapshot(si, vm.snapshot.currentSnapshot)
            time.sleep(10)
    except KeyboardInterrupt:
        cost_file.close()
    '''


def get_snapshot_size(vsphere_vm):
    """returns snapshot size, in GB for a VM"""
    disk_list = vsphere_vm.layoutEx.file
    size = 0
    for disk in disk_list:
        if disk.type == 'snapshotData':
            size += disk.size

        #  扫描整个字符串并返回第一个成功的匹配。
        ss_disk = re.search('0000\d\d', disk.name)
        if ss_disk:
            size += disk.size

    size_gb = (float(size) / 1024 / 1024 / 1024)
    print round(size_gb, 2)