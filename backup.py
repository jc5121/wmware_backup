#!/usr/env python

from pyvddk import *
import time
import json
from pyVmomi import vim, vmodl


# change 3 file every restore
FULL_BACKUPFILE = '2019-05-08-21-43-06.vmdk'
INCREMENTAL_BACKUPFILE = '2019-05-09-00-42-11.dat'
CBI_FILE = '2019-05-09-00-42-11-cbi.json'

CHANGEIDFILE = 'changeID.log'
DIR_SEP = 'diskfile/'
TIME = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

REMOTE_DISK = '[vSanMgmt] f078d25c-f69a-52d5-3929-ecf4bbe05190/jchao-232.vmdk'
VIXDISKLIB_PATH = '/usr/lib/vmware-vix-disklib/'

kwargs_vc = {
    'vmxSpec': 'moref=vm-189',
    'server': '10.155.20.2',
    'port': 443,
    'thumbPrint': 'F8:A1:69:46:16:B3:DC:09:45:A5:3B:69:1F:F5:DF:B1:90:64:7B:70',
    'user': 'administrator@vsphere.local',
    'password': 'VMware1!',
    'vimApiVer': None,
    'dataCenter': 'VIO',
    'folder': '/',
    'vmName': 'jchao-232'
}
c_type = CFUNCTYPE(None, c_void_p)


def log_fucn(log):
    # write log to a file
    # print log
    return 0


def do_create():
    print "create success-------------------------------------------"
    return 0


# dump metadata of a disk
def get_meta():

    Init(6, 5, LOGGERTYPE(log_fucn), LOGGERTYPE(log_fucn), LOGGERTYPE(log_fucn), VIXDISKLIB_PATH)
    vddk = VixDiskLib()
    vddk.Connect(**kwargs_vc)

    # remote disk file
    remote_disk = vddk.Open(REMOTE_DISK, VIXDISKLIB_FLAG_OPEN_READ_ONLY)
    meta_keys = remote_disk.GetMetadataKeys()
    for key in meta_keys:
        print key+':', remote_disk.ReadMetadata(key)
    remote_disk.Close()
    vddk.Disconnect()
    Exit()


def full_backup(vm):

    if vm.snapshot is None:
        print 'no snapshot'
        sys.exit()
    for device in vm.snapshot.currentSnapshot.config.hardware.device:
        if isinstance(device.backing, vim.vm.device.VirtualDisk.FlatVer2BackingInfo):
            new_changeID = device.backing.changeId

    Init(6, 5, LOGGERTYPE(log_fucn), LOGGERTYPE(log_fucn), LOGGERTYPE(log_fucn), VIXDISKLIB_PATH)
    vddk = VixDiskLib()
    vddk.Connect(**kwargs_vc)

    # remote disk file
    remote_disk = vddk.Open(REMOTE_DISK, VIXDISKLIB_FLAG_OPEN_READ_ONLY)
    adapter = remote_disk.GetInfo().get('adapterType', 3)
    capacity = remote_disk.GetInfo().get('capacity', None)


    # local disk file
    file_name = DIR_SEP + TIME + '.vmdk'
    vddk.Create_local(file_name, VIXDISKLIB_DISK_MONOLITHIC_SPARSE, adapter,
                       VIXDISKLIB_HWVERSION_WORKSTATION_5, capacity, VixDiskLibProgressFunc(do_create), None)
    local_disk = vddk.open_local(file_name, VIXDISKLIB_FLAG_OPEN_SINGLE_LINK)

    # read from remote and write to local
    count = 1024
    max_ops = capacity / count
    print 'Processing ' + str(max_ops) + ' buffers of ' + str(count * VIXDISKLIB_SECTOR_SIZE) + ' bytes.'
    for i in range(max_ops):
        buf = remote_disk.Read(i * count, count)
        raw_bytes = (c_ubyte * len(buf)).from_buffer_copy(buf)
        # local_file.write(raw_bytes)
        local_disk.Write(i * count, raw_bytes)
        print str(i) + ' ' + str(max_ops) + ' : ' + str(len(buf))

    load_changeID(new_changeID)
    remote_disk.Close()
    local_disk.Close()
    # local_file.close()
    vddk.Disconnect()
    Exit()


def full_restore(vm):

    if vm.snapshot is None:
        print 'no snapshot'
        sys.exit()

    Init(6, 5, LOGGERTYPE(log_fucn), LOGGERTYPE(log_fucn), LOGGERTYPE(log_fucn), VIXDISKLIB_PATH)
    vddk = VixDiskLib()
    vddk.Connect(**kwargs_vc)

    # remote disk file
    remote_disk = vddk.Open(REMOTE_DISK,
                            VIXDISKLIB_FLAG_OPEN_SINGLE_LINK)
    adapter = remote_disk.GetInfo().get('adapterType', 3)
    capacity = remote_disk.GetInfo().get('capacity', None)

    # local disk file
    file_name = DIR_SEP + FULL_BACKUPFILE
    #file_name = 'diskfile/20190505005912.vmdk'
    local_disk = vddk.open_local(file_name, VIXDISKLIB_FLAG_OPEN_READ_ONLY)

    # read from remote and write to local
    count = 1024
    max_ops = capacity / count
    print 'Processing ' + str(max_ops) + ' buffers of ' + str(count * VIXDISKLIB_SECTOR_SIZE) + ' bytes.'
    for i in range(max_ops):
        buf = local_disk.Read(i * count, count)
        raw_bytes = (c_ubyte * len(buf)).from_buffer_copy(buf)
        remote_disk.Write(i * count, raw_bytes)
        print str(i) + ' ' + str(max_ops) + ' : ' + str(len(buf))

    remote_disk.Close()
    local_disk.Close()
    # local_file.close()
    vddk.Disconnect()
    Exit()


def incremental_backup(vm):

    start_time = time.time()

    if vm.snapshot is None:
        print 'no snapshot'
        sys.exit()

    Init(6, 5, LOGGERTYPE(log_fucn), LOGGERTYPE(log_fucn), LOGGERTYPE(log_fucn), VIXDISKLIB_PATH)
    vddk = VixDiskLib()
    vddk.Connect(**kwargs_vc)
    remote_disk = vddk.Open(REMOTE_DISK, VIXDISKLIB_FLAG_OPEN_READ_ONLY)

    # print remote_disk.GetInfo().get('capacity', None) 73400320
    last_changeID = get_changeID()
    new_changeID = do_incremental_backup(remote_disk, vm, last_changeID)
    load_changeID(new_changeID)

    end_time = time.time()
    print "Backup done, costing %f s" % (end_time - start_time)
    # python release those resources?
    #remote_disk.Close()
    #vddk.Disconnect()
    #Exit()


def do_incremental_backup(disk, vm, last_changeID):

    for device in vm.snapshot.currentSnapshot.config.hardware.device:
        if isinstance(device.backing, vim.vm.device.VirtualDisk.FlatVer2BackingInfo):
            new_changeID = device.backing.changeId
            capacity = device.capacityInKB * 1024
            device_key = device.key

    print 'last_changeID: ' + last_changeID
    print 'new_changeID: ' + new_changeID
    if new_changeID == last_changeID:
        print 'same changeID, use new snapshot.'
        sys.exit()
    snapshot = vm.snapshot.currentSnapshot
    start_position = 0

    #filename = DIR_SEP + INCREMENTAL_BACKUPFILE
    filename = DIR_SEP + TIME + '.dat'
    local_file = open(filename, 'wb')
    size_sum = 0

    cbi_list = list()

    #temp_changeID = '52 8a b4 5c 7b ab 8e 51-7a 73 16 d1 76 9a 0d a6/2'
    while start_position < capacity:
        changes = vm.QueryChangedDiskAreas(snapshot, device_key, start_position, last_changeID)
        #changes = vm.QueryChangedDiskAreas(snapshot, device_key, start_position, temp_changeID)
        print '--------------------------'
        for area in changes.changedArea:

            cbi_list.append((area.start, area.length))
            count = area.length / VIXDISKLIB_SECTOR_SIZE
            start_sector = area.start / VIXDISKLIB_SECTOR_SIZE
            buf = disk.Read(start_sector, count)
            local_file.write(buf)
            size_sum += len(buf)
        start_position = changes.startOffset + changes.length

    print size_sum
    dump_CBI(cbi_list)
    local_file.close()
    return new_changeID


def incremental_restore(vm):

    start_time = time.time()
    if vm.snapshot is None:
        print 'no snapshot'
        sys.exit()

    Init(6, 5, LOGGERTYPE(log_fucn), LOGGERTYPE(log_fucn), LOGGERTYPE(log_fucn), VIXDISKLIB_PATH)
    vddk = VixDiskLib()
    vddk.Connect(**kwargs_vc)
    remote_disk = vddk.Open(REMOTE_DISK, VIXDISKLIB_FLAG_OPEN_SINGLE_LINK)

    do_incremental_restore(remote_disk)

    end_time = time.time()
    print "Restore done, costing %f s" % (end_time - start_time)

    # python release those resources?
    #remote_disk.Close()
    #vddk.Disconnect()
    #Exit()


def do_incremental_restore(disk):

    filename = DIR_SEP + INCREMENTAL_BACKUPFILE
    local_file = open(filename, 'rb')
    size_sum = 0
    offset = 0

    cbi_list = get_CBI()
    for area in cbi_list:
        start_sector = area[0] / VIXDISKLIB_SECTOR_SIZE
        local_file.seek(offset)
        buf = local_file.read(area[1])
        size_sum += len(buf)
        offset += area[1]
        raw_bytes = (c_ubyte * len(buf)).from_buffer_copy(buf)
        # print area.start, area.length
        disk.Write(start_sector, raw_bytes)
        # print '1'


# store the changed-block information to a json file
def dump_CBI(CBI_dic):
    info = json.dumps(CBI_dic)

    CBI_file = DIR_SEP + TIME + '.json'
    with open(CBI_file, 'w') as f:
        f.write(info)


def get_CBI():

    CBI_file = DIR_SEP + CBI_FILE
    with open(CBI_file, 'r') as f:
        CBI_list = json.load(f)

    #print CBI_list
    return CBI_list


def get_changeID():
    filename = DIR_SEP + CHANGEIDFILE
    with open(filename, 'r') as f:
        line = f.readline()
        changeID = line
        #print changeID
    return changeID


def load_changeID(changeID):
    filename = DIR_SEP + CHANGEIDFILE
    changeID_file = open(filename, 'w+')
    line = changeID_file.readline()
    if changeID == line:
        print 'same changeID, use new snapshot'

    else:
        changeID_file.write(changeID)
    changeID_file.close()


def update_changeID(vm):
    """
    update the ChangeID of the current snapshot
    """

    if vm.snapshot is None:
        print 'no snapshot'
        sys.exit()

    for device in vm.snapshot.currentSnapshot.config.hardware.device:
        if isinstance(device.backing, vim.vm.device.VirtualDisk.FlatVer2BackingInfo):
            changeID =  device.backing.changeId

    print changeID
    #load_changeID(changeID)

    print 'Done'


if __name__ == '__main__':
    # get_meta()
    # full_backup()
    # incremental_backup(None)
    # get_meta()
    # get_CBI()

    print 'costing %f ms' % (1.21541841)

