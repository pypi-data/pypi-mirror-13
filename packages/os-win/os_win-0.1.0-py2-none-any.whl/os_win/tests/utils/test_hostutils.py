#  Copyright 2014 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
from oslotest import base

from os_win import constants
from os_win import exceptions
from os_win.utils import hostutils


class FakeCPUSpec(object):
    """Fake CPU Spec for unit tests."""

    Architecture = mock.sentinel.cpu_arch
    Name = mock.sentinel.cpu_name
    Manufacturer = mock.sentinel.cpu_man
    NumberOfCores = mock.sentinel.cpu_cores
    NumberOfLogicalProcessors = mock.sentinel.cpu_procs


class HostUtilsTestCase(base.BaseTestCase):
    """Unit tests for the Hyper-V hostutils class."""

    _DEVICE_ID = "Microsoft:UUID\\0\\0"
    _NODE_ID = "Microsoft:PhysicalNode\\0"

    _FAKE_MEMORY_TOTAL = 1024
    _FAKE_MEMORY_FREE = 512
    _FAKE_DISK_SIZE = 1024
    _FAKE_DISK_FREE = 512
    _FAKE_VERSION_GOOD = '6.2.0'
    _FAKE_VERSION_BAD = '6.1.9'

    def setUp(self):
        self._hostutils = hostutils.HostUtils()
        self._hostutils._conn_cimv2 = mock.MagicMock()
        self._hostutils._virt_v2 = mock.MagicMock()

        super(HostUtilsTestCase, self).setUp()

    @mock.patch.object(hostutils, 'wmi', create=True)
    def test_init_wmi_virt_conn(self, mock_wmi):
        self._hostutils._init_wmi_virt_conn()

        self.assertEqual(mock_wmi.WMI.return_value, self._hostutils._virt_v2)
        mock_wmi.WMI.assert_called_once_with(
            moniker='//./root/virtualization/v2')

    @mock.patch.object(hostutils, 'wmi', create=True)
    def test_init_wmi_virt_conn_exception(self, mock_wmi):
        self._hostutils._virt_v2 = None
        mock_wmi.WMI.side_effect = Exception

        self._hostutils._init_wmi_virt_conn()
        self.assertIsNone(self._hostutils._virt_v2)

    def test_conn_virt(self):
        self._hostutils._virt_v2 = mock.sentinel.conn
        self.assertEqual(mock.sentinel.conn, self._hostutils._conn_virt)

    def test_conn_virt_uninitialized(self):
        self._hostutils._virt_v2 = None
        self.assertRaises(exceptions.HyperVException,
                          getattr, self._hostutils, '_conn_virt')

    @mock.patch('os_win.utils.hostutils.ctypes')
    def test_get_host_tick_count64(self, mock_ctypes):
        tick_count64 = "100"
        mock_ctypes.windll.kernel32.GetTickCount64.return_value = tick_count64
        response = self._hostutils.get_host_tick_count64()
        self.assertEqual(tick_count64, response)

    def test_get_cpus_info(self):
        cpu = mock.MagicMock(spec=FakeCPUSpec)
        self._hostutils._conn_cimv2.query.return_value = [cpu]
        cpu_list = self._hostutils.get_cpus_info()
        self.assertEqual([cpu._mock_children], cpu_list)

    def test_get_memory_info(self):
        memory = mock.MagicMock()
        type(memory).TotalVisibleMemorySize = mock.PropertyMock(
            return_value=self._FAKE_MEMORY_TOTAL)
        type(memory).FreePhysicalMemory = mock.PropertyMock(
            return_value=self._FAKE_MEMORY_FREE)

        self._hostutils._conn_cimv2.query.return_value = [memory]
        total_memory, free_memory = self._hostutils.get_memory_info()

        self.assertEqual(self._FAKE_MEMORY_TOTAL, total_memory)
        self.assertEqual(self._FAKE_MEMORY_FREE, free_memory)

    def test_get_volume_info(self):
        disk = mock.MagicMock()
        type(disk).Size = mock.PropertyMock(return_value=self._FAKE_DISK_SIZE)
        type(disk).FreeSpace = mock.PropertyMock(
            return_value=self._FAKE_DISK_FREE)

        self._hostutils._conn_cimv2.query.return_value = [disk]
        (total_memory, free_memory) = self._hostutils.get_volume_info(
            mock.sentinel.FAKE_DRIVE)

        self.assertEqual(self._FAKE_DISK_SIZE, total_memory)
        self.assertEqual(self._FAKE_DISK_FREE, free_memory)

    def test_check_min_windows_version_true(self):
        self._test_check_min_windows_version(self._FAKE_VERSION_GOOD, True)

    def test_check_min_windows_version_false(self):
        self._test_check_min_windows_version(self._FAKE_VERSION_BAD, False)

    def _test_check_min_windows_version(self, version, expected):
        os = mock.MagicMock()
        os.Version = version
        self._hostutils._conn_cimv2.Win32_OperatingSystem.return_value = [os]
        hostutils.HostUtils._windows_version = None
        self.assertEqual(expected,
                         self._hostutils.check_min_windows_version(6, 2))

    def test_get_windows_version(self):
        os = mock.MagicMock()
        os.Version = self._FAKE_VERSION_GOOD
        self._hostutils._conn_cimv2.Win32_OperatingSystem.return_value = [os]
        hostutils.HostUtils._windows_version = None
        self.assertEqual(self._FAKE_VERSION_GOOD,
                         self._hostutils.get_windows_version())

    def _test_host_power_action(self, action):
        fake_win32 = mock.MagicMock()
        fake_win32.Win32Shutdown = mock.MagicMock()

        self._hostutils._conn_cimv2.Win32_OperatingSystem.return_value = [
            fake_win32]

        if action == constants.HOST_POWER_ACTION_SHUTDOWN:
            self._hostutils.host_power_action(action)
            fake_win32.Win32Shutdown.assert_called_with(
                self._hostutils._HOST_FORCED_SHUTDOWN)
        elif action == constants.HOST_POWER_ACTION_REBOOT:
            self._hostutils.host_power_action(action)
            fake_win32.Win32Shutdown.assert_called_with(
                self._hostutils._HOST_FORCED_REBOOT)
        else:
            self.assertRaises(NotImplementedError,
                              self._hostutils.host_power_action, action)

    def test_host_shutdown(self):
        self._test_host_power_action(constants.HOST_POWER_ACTION_SHUTDOWN)

    def test_host_reboot(self):
        self._test_host_power_action(constants.HOST_POWER_ACTION_REBOOT)

    def test_host_startup(self):
        self._test_host_power_action(constants.HOST_POWER_ACTION_STARTUP)

    def test_get_supported_vm_types_2012_r2(self):
        with mock.patch.object(self._hostutils,
                               'check_min_windows_version') as mock_check_win:
            mock_check_win.return_value = True
            result = self._hostutils.get_supported_vm_types()
            self.assertEqual([constants.IMAGE_PROP_VM_GEN_1,
                              constants.IMAGE_PROP_VM_GEN_2], result)

    def test_get_supported_vm_types(self):
        with mock.patch.object(self._hostutils,
                               'check_min_windows_version') as mock_check_win:
            mock_check_win.return_value = False
            result = self._hostutils.get_supported_vm_types()
            self.assertEqual([constants.IMAGE_PROP_VM_GEN_1], result)

    def test_check_server_feature(self):
        mock_sv_feature_cls = self._hostutils._conn_cimv2.Win32_ServerFeature
        mock_sv_feature_cls.return_value = [mock.sentinel.sv_feature]

        feature_enabled = self._hostutils.check_server_feature(
            mock.sentinel.feature_id)
        self.assertTrue(feature_enabled)

        mock_sv_feature_cls.assert_called_once_with(
            ID=mock.sentinel.feature_id)

    def _check_get_numa_nodes_missing_info(self):
        numa_node = mock.MagicMock()
        self._hostutils._conn_virt.Msvm_NumaNode.return_value = [
            numa_node, numa_node]

        nodes_info = self._hostutils.get_numa_nodes()
        self.assertEqual([], nodes_info)

    @mock.patch.object(hostutils.HostUtils, '_get_numa_memory_info')
    def test_get_numa_nodes_missing_memory_info(self, mock_get_memory_info):
        mock_get_memory_info.return_value = None
        self._check_get_numa_nodes_missing_info()

    @mock.patch.object(hostutils.HostUtils, '_get_numa_cpu_info')
    @mock.patch.object(hostutils.HostUtils, '_get_numa_memory_info')
    def test_get_numa_nodes_missing_cpu_info(self, mock_get_memory_info,
                                             mock_get_cpu_info):
        mock_get_cpu_info.return_value = None
        self._check_get_numa_nodes_missing_info()

    @mock.patch.object(hostutils.HostUtils, '_get_numa_cpu_info')
    @mock.patch.object(hostutils.HostUtils, '_get_numa_memory_info')
    def test_get_numa_nodes(self, mock_get_memory_info, mock_get_cpu_info):
        numa_memory = mock_get_memory_info.return_value
        host_cpu = mock.MagicMock(DeviceID=self._DEVICE_ID)
        mock_get_cpu_info.return_value = [host_cpu]
        numa_node = mock.MagicMock(NodeID=self._NODE_ID)
        numa_node.associators.return_value = [numa_memory, host_cpu]
        self._hostutils._conn_virt.Msvm_NumaNode.return_value = [
            numa_node, numa_node]

        nodes_info = self._hostutils.get_numa_nodes()

        expected_info = {
            'id': self._DEVICE_ID.split('\\')[-1],
            'memory': numa_memory.NumberOfBlocks,
            'memory_usage': numa_node.CurrentlyConsumableMemoryBlocks,
            'cpuset': set([self._DEVICE_ID.split('\\')[-1]]),
            'cpu_usage': 0,
        }

        self.assertEqual([expected_info, expected_info], nodes_info)

    def test_get_numa_memory_info(self):
        numa_memory = mock.MagicMock()
        numa_node = mock.MagicMock()
        numa_node.associators.return_value = [numa_memory]
        memory_info = self._hostutils._get_numa_memory_info(numa_node)

        self.assertEqual(numa_memory, memory_info)

    def test_get_numa_memory_info_not_found(self):
        numa_node = mock.MagicMock()
        numa_node.associators.return_value = []
        memory_info = self._hostutils._get_numa_memory_info(numa_node)

        self.assertIsNone(memory_info)

    def test_get_numa_cpu_info(self):
        host_cpu = mock.MagicMock()
        host_cpu.path_.return_value = 'fake_wmi_obj_path'
        vm_cpu = mock.MagicMock()
        vm_cpu.path_return_value = 'fake_wmi_obj_path1'
        numa_node_proc_path = ['fake_wmi_obj_path']
        cpu_info = self._hostutils._get_numa_cpu_info(numa_node_proc_path,
                                                      [host_cpu, vm_cpu])

        self.assertEqual([host_cpu], cpu_info)

    def test_get_numa_cpu_info_not_found(self):
        other = mock.MagicMock()
        cpu_info = self._hostutils._get_numa_cpu_info([], [other])

        self.assertEqual([], cpu_info)
