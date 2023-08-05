# Copyright 2014, 2015 IBM Corp.
#
# All Rights Reserved.
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
#

import logging

import mock
from oslo_config import cfg
from oslo_serialization import jsonutils

from nova import block_device as nova_block_device
from nova import exception as exc
from nova import objects
from nova.objects import block_device as bdmobj
from nova import test
from nova.tests.unit import fake_instance
from nova.virt import block_device as nova_virt_bdm
from nova.virt import fake
import pypowervm.adapter as pvm_adp
import pypowervm.exceptions as pvm_exc
import pypowervm.tests.test_fixtures as pvm_fx
from pypowervm.tests.test_utils import pvmhttp
import pypowervm.utils.transaction as pvm_tx
import pypowervm.wrappers.base_partition as pvm_bp
import pypowervm.wrappers.logical_partition as pvm_lpar
import pypowervm.wrappers.managed_system as pvm_ms
import pypowervm.wrappers.virtual_io_server as pvm_vios

from nova_powervm.tests.virt import powervm
from nova_powervm.tests.virt.powervm import fixtures as fx
from nova_powervm.virt.powervm import driver
from nova_powervm.virt.powervm import exception as p_exc
from nova_powervm.virt.powervm import live_migration as lpm

MS_HTTPRESP_FILE = "managedsystem.txt"
MS_NAME = 'HV4'
LPAR_HTTPRESP_FILE = "lpar.txt"
VIOS_HTTPRESP_FILE = "fake_vios_ssp_npiv.txt"

LOG = logging.getLogger(__name__)
logging.basicConfig()

CONF = cfg.CONF
CONF.import_opt('my_ip', 'nova.netconf')


class FakeClass(object):
    """Used for the test_inst_dict."""
    pass


class TestPowerVMDriver(test.TestCase):
    def setUp(self):
        super(TestPowerVMDriver, self).setUp()

        ms_http = pvmhttp.load_pvm_resp(MS_HTTPRESP_FILE)
        self.assertIsNotNone(ms_http, "Could not load %s " % MS_HTTPRESP_FILE)

        entries = ms_http.response.feed.findentries(pvm_ms._SYSTEM_NAME,
                                                    MS_NAME)

        self.assertNotEqual(entries, None,
                            "Could not find %s in %s" %
                            (MS_NAME, MS_HTTPRESP_FILE))

        self.wrapper = pvm_ms.System.wrap(entries[0])

        self.flags(disk_driver='localdisk', group='powervm')
        self.drv_fix = self.useFixture(fx.PowerVMComputeDriver())
        self.drv = self.drv_fix.drv
        self.apt = self.drv.adapter

        self._setup_lpm()

        self.disk_dvr = self.drv.disk_dvr
        self.vol_fix = self.useFixture(fx.VolumeAdapter())
        self.vol_drv = self.vol_fix.drv

        self.crt_lpar_p = mock.patch('nova_powervm.virt.powervm.vm.crt_lpar')
        self.crt_lpar = self.crt_lpar_p.start()
        self.addCleanup(self.crt_lpar_p.stop)

        self.get_inst_wrap_p = mock.patch('nova_powervm.virt.powervm.vm.'
                                          'get_instance_wrapper')
        self.get_inst_wrap = self.get_inst_wrap_p.start()
        self.addCleanup(self.get_inst_wrap_p.stop)

        wrap = pvm_lpar.LPAR.wrap(pvmhttp.load_pvm_resp(
            LPAR_HTTPRESP_FILE).response)[0]
        self.crt_lpar.return_value = wrap
        self.get_inst_wrap.return_value = wrap

        self.build_tx_feed_p = mock.patch('nova_powervm.virt.powervm.vios.'
                                          'build_tx_feed_task')
        self.build_tx_feed = self.build_tx_feed_p.start()
        self.addCleanup(self.build_tx_feed_p.stop)
        self.useFixture(pvm_fx.FeedTaskFx([pvm_vios.VIOS.wrap(
            pvmhttp.load_pvm_resp(VIOS_HTTPRESP_FILE).response)]))
        self.stg_ftsk = pvm_tx.FeedTask('fake', pvm_vios.VIOS.getter(self.apt))
        self.build_tx_feed.return_value = self.stg_ftsk

        scrub_stg_p = mock.patch('pypowervm.tasks.storage.'
                                 'add_lpar_storage_scrub_tasks')
        self.scrub_stg = scrub_stg_p.start()
        self.addCleanup(scrub_stg_p.stop)

    def _setup_lpm(self):
        """Setup the lpm environment.

        This may have to be called directly by tests since the lpm code
        cleans up the dict entry on the last expected lpm method.
        """
        self.lpm = mock.Mock()
        self.lpm_inst = mock.Mock()
        self.lpm_inst.uuid = 'inst1'
        self.drv.live_migrations = {'inst1': self.lpm}

    def test_driver_create(self):
        """Validates that a driver of the PowerVM type can be initialized."""
        test_drv = driver.PowerVMDriver(fake.FakeVirtAPI())
        self.assertIsNotNone(test_drv)

    def test_get_volume_connector(self):
        """Tests that a volume connector can be built."""
        vol_connector = self.drv.get_volume_connector(mock.Mock())
        self.assertIsNotNone(vol_connector['wwpns'])
        self.assertIsNotNone(vol_connector['host'])

    @mock.patch('nova_powervm.virt.powervm.vm.get_pvm_uuid')
    @mock.patch('nova.context.get_admin_context')
    def test_driver_ops(self, mock_get_ctx, mock_getuuid):
        """Validates the PowerVM driver operations."""
        # get_info()
        inst = fake_instance.fake_instance_obj(mock.sentinel.ctx)
        mock_getuuid.return_value = '1234'
        info = self.drv.get_info(inst)
        self.assertEqual(info.id, '1234')

        # list_instances()
        tgt_mock = 'nova_powervm.virt.powervm.vm.get_lpar_names'
        with mock.patch(tgt_mock) as mock_get_list:
            fake_lpar_list = ['1', '2']
            mock_get_list.return_value = fake_lpar_list
            inst_list = self.drv.list_instances()
            self.assertEqual(fake_lpar_list, inst_list)

        # instance_exists()
        tgt_mock = 'nova_powervm.virt.powervm.vm.instance_exists'
        with mock.patch(tgt_mock) as mock_inst_exists:
            mock_inst_exists.side_effect = [True, False]
            self.assertTrue(self.drv.instance_exists(mock.Mock()))
            self.assertFalse(self.drv.instance_exists(mock.Mock()))

    @mock.patch('nova_powervm.virt.powervm.tasks.storage.'
                'CreateAndConnectCfgDrive.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.storage.ConnectVolume'
                '.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.storage.CreateDiskForImg'
                '.execute')
    @mock.patch('nova_powervm.virt.powervm.driver.PowerVMDriver.'
                '_is_booted_from_volume')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugMgmtVif.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugVifs.execute')
    @mock.patch('nova.virt.configdrive.required_by')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    @mock.patch('pypowervm.tasks.power.power_on')
    def test_spawn_ops(
        self, mock_pwron, mock_get_flv, mock_cfg_drv, mock_plug_vifs,
        mock_plug_mgmt_vif, mock_boot_from_vol, mock_crt_disk_img,
        mock_conn_vol, mock_crt_cfg_drv):
        """Validates the 'typical' spawn flow of the spawn of an instance.

        Uses a basic disk image, attaching networks and powering on.
        """
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.system_metadata = {'image_os_distro': 'rhel'}
        my_flavor = inst.get_flavor()
        mock_get_flv.return_value = my_flavor
        mock_cfg_drv.return_value = False
        mock_boot_from_vol.return_value = False
        # Invoke the method.
        self.drv.spawn('context', inst, mock.Mock(),
                       'injected_files', 'admin_password')

        # Assert the correct tasks were called
        self.assertTrue(mock_plug_vifs.called)
        self.assertTrue(mock_plug_mgmt_vif.called)
        self.assertTrue(mock_crt_disk_img.called)
        self.crt_lpar.assert_called_with(
            self.apt, self.drv.host_wrapper, inst, my_flavor)
        self.assertTrue(mock_pwron.called)
        self.assertFalse(mock_pwron.call_args[1]['synchronous'])
        # Assert that tasks that are not supposed to be called are not called
        self.assertFalse(mock_conn_vol.called)
        self.assertFalse(mock_crt_cfg_drv.called)
        self.scrub_stg.assert_called_with([9], self.stg_ftsk, lpars_exist=True)

    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugMgmtVif.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugVifs.execute')
    @mock.patch('nova_powervm.virt.powervm.media.ConfigDrivePowerVM.'
                'create_cfg_drv_vopt')
    @mock.patch('nova_powervm.virt.powervm.media.ConfigDrivePowerVM.'
                '_validate_vopt_vg')
    @mock.patch('nova.virt.configdrive.required_by')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    @mock.patch('pypowervm.tasks.power.power_on')
    def test_spawn_with_cfg(
        self, mock_pwron, mock_get_flv, mock_cfg_drv, mock_val_vopt,
        mock_cfg_vopt, mock_plug_vifs, mock_plug_mgmt_vif):
        """Validates the PowerVM spawn w/ config drive operations."""
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.system_metadata = {'image_os_distro': 'rhel'}
        my_flavor = inst.get_flavor()
        mock_get_flv.return_value = my_flavor
        mock_cfg_drv.return_value = True

        # Invoke the method.
        self.drv.spawn('context', inst, mock.Mock(),
                       'injected_files', 'admin_password')

        # Create LPAR was called
        self.crt_lpar.assert_called_with(self.apt, self.drv.host_wrapper,
                                         inst, my_flavor)
        # Config drive was called
        self.assertTrue(mock_val_vopt.called)
        self.assertTrue(mock_cfg_vopt.called)

        # Power on was called
        self.assertTrue(mock_pwron.called)
        self.assertFalse(mock_pwron.call_args[1]['synchronous'])
        self.scrub_stg.assert_called_with([9], self.stg_ftsk, lpars_exist=True)

    @mock.patch('nova.virt.block_device.DriverVolumeBlockDevice.save')
    @mock.patch('nova_powervm.virt.powervm.tasks.storage.CreateDiskForImg'
                '.execute')
    @mock.patch('nova_powervm.virt.powervm.driver.PowerVMDriver.'
                '_is_booted_from_volume')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugMgmtVif.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugVifs.execute')
    @mock.patch('nova.virt.configdrive.required_by')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    @mock.patch('pypowervm.tasks.power.power_on')
    def test_spawn_with_bdms(
        self, mock_pwron, mock_get_flv, mock_cfg_drv, mock_plug_vifs,
        mock_plug_mgmt_vif, mock_boot_from_vol, mock_crt_img, mock_save):
        """Validates the PowerVM spawn.

        Specific Test: spawn of an image that has a disk image and block device
        mappings are passed into spawn which originated from either the image
        metadata itself or the create server request. In particular, test when
        the BDMs passed in do not have the root device for the instance.
        """
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.system_metadata = {'image_os_distro': 'rhel'}
        my_flavor = inst.get_flavor()
        mock_get_flv.return_value = my_flavor
        mock_cfg_drv.return_value = False
        mock_boot_from_vol.return_value = False

        # Create some fake BDMs
        block_device_info = self._fake_bdms()

        # Invoke the method.
        self.drv.spawn('context', inst, mock.Mock(),
                       'injected_files', 'admin_password',
                       block_device_info=block_device_info)

        self.assertTrue(mock_boot_from_vol.called)
        # Since the root device is not in the BDMs we expect the image disk to
        # be created.
        self.assertTrue(mock_crt_img.called)

        # Create LPAR was called
        self.crt_lpar.assert_called_with(self.apt, self.drv.host_wrapper,
                                         inst, my_flavor)
        # Power on was called
        self.assertTrue(mock_pwron.called)
        self.assertFalse(mock_pwron.call_args[1]['synchronous'])

        # Check that the connect volume was called
        self.assertEqual(2, self.vol_drv.connect_volume.call_count)

        # Make sure the save was invoked
        self.assertEqual(2, mock_save.call_count)

        self.scrub_stg.assert_called_with([9], self.stg_ftsk, lpars_exist=True)

    @mock.patch('nova.virt.block_device.DriverVolumeBlockDevice.save')
    @mock.patch('nova_powervm.virt.powervm.tasks.storage.CreateDiskForImg'
                '.execute')
    @mock.patch('nova_powervm.virt.powervm.driver.PowerVMDriver.'
                '_is_booted_from_volume')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugMgmtVif.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugVifs.execute')
    @mock.patch('nova.virt.configdrive.required_by')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    @mock.patch('pypowervm.tasks.power.power_on')
    def test_spawn_with_image_meta_root_bdm(
        self, mock_pwron, mock_get_flv, mock_cfg_drv, mock_plug_vifs,
        mock_plug_mgmt_vif, mock_boot_from_vol, mock_crt_img, mock_save):

        """Validates the PowerVM spawn.

        Specific Test: spawn of an image that does not have a disk image but
        rather the block device mappings are passed into spawn.  These
        originated from either the image metadata itself or the create server
        request.  In particular, test when the BDMs passed in have the root
        device for the instance and image metadata from an image is also
        passed.

        Note this tests the ability to spawn an image that does not
        contain a disk image but rather contains block device mappings
        containing the root BDM. The
        nova.compute.api.API.snapshot_volume_backed flow produces such images.
        """
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.system_metadata = {'image_os_distro': 'rhel'}
        my_flavor = inst.get_flavor()
        mock_get_flv.return_value = my_flavor
        mock_cfg_drv.return_value = False
        mock_boot_from_vol.return_value = True

        # Create some fake BDMs
        block_device_info = self._fake_bdms()
        image_meta = {'id': 'imageuuid'}
        # Invoke the method.
        self.drv.spawn('context', inst, image_meta,
                       'injected_files', 'admin_password',
                       block_device_info=block_device_info)

        self.assertTrue(mock_boot_from_vol.called)
        # Since the root device is in the BDMs we do not expect the image disk
        # to be created.
        self.assertFalse(mock_crt_img.called)

        # Create LPAR was called
        self.crt_lpar.assert_called_with(self.apt, self.drv.host_wrapper,
                                         inst, my_flavor)
        # Power on was called
        self.assertTrue(mock_pwron.called)
        self.assertFalse(mock_pwron.call_args[1]['synchronous'])

        # Check that the connect volume was called
        self.assertEqual(2, self.vol_drv.connect_volume.call_count)

        self.scrub_stg.assert_called_with([9], self.stg_ftsk, lpars_exist=True)

    @mock.patch('nova.virt.block_device.DriverVolumeBlockDevice.save')
    @mock.patch('nova_powervm.virt.powervm.tasks.storage.CreateDiskForImg'
                '.execute')
    @mock.patch('nova_powervm.virt.powervm.driver.PowerVMDriver.'
                '_is_booted_from_volume')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugMgmtVif.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugVifs.execute')
    @mock.patch('nova.virt.configdrive.required_by')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    @mock.patch('pypowervm.tasks.power.power_on')
    def test_spawn_with_root_bdm(
        self, mock_pwron, mock_get_flv, mock_cfg_drv, mock_plug_vifs,
        mock_plug_mgmt_vif, mock_boot_from_vol, mock_crt_img, mock_save):
        """Validates the PowerVM spawn.

        Specific test: when no image is given and only block device mappings
        are given on the create server request.
        """
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.system_metadata = {'image_os_distro': 'rhel'}
        my_flavor = inst.get_flavor()
        mock_get_flv.return_value = my_flavor
        mock_cfg_drv.return_value = False
        mock_boot_from_vol.return_value = True

        # Create some fake BDMs
        block_device_info = self._fake_bdms()
        image_meta = {}
        # Invoke the method.
        self.drv.spawn('context', inst, image_meta,
                       'injected_files', 'admin_password',
                       block_device_info=block_device_info)

        self.assertTrue(mock_boot_from_vol.called)
        # Since the root device is in the BDMs we do not expect the image disk
        # to be created.
        self.assertFalse(mock_crt_img.called)

        # Create LPAR was called
        self.crt_lpar.assert_called_with(self.apt, self.drv.host_wrapper,
                                         inst, my_flavor)
        # Power on was called
        self.assertTrue(mock_pwron.called)
        self.assertFalse(mock_pwron.call_args[1]['synchronous'])

        # Check that the connect volume was called
        self.assertEqual(2, self.vol_drv.connect_volume.call_count)

        # Make sure the BDM save was invoked twice.
        self.assertEqual(2, mock_save.call_count)

        self.scrub_stg.assert_called_with([9], self.stg_ftsk, lpars_exist=True)

    @mock.patch('nova.virt.block_device.DriverVolumeBlockDevice.save')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugMgmtVif.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugVifs.execute')
    @mock.patch('nova_powervm.virt.powervm.vm.dlt_lpar')
    @mock.patch('nova.virt.configdrive.required_by')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    @mock.patch('pypowervm.tasks.power.power_on')
    @mock.patch('pypowervm.tasks.power.power_off')
    def test_spawn_ops_rollback(
        self, mock_pwroff, mock_pwron, mock_get_flv, mock_cfg_drv, mock_dlt,
        mock_plug_vifs, mock_plug_mgmt_vifs, mock_save):
        """Validates the PowerVM driver operations.  Will do a rollback."""
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.system_metadata = {'image_os_distro': 'rhel'}
        my_flavor = inst.get_flavor()
        mock_get_flv.return_value = my_flavor
        mock_cfg_drv.return_value = False
        block_device_info = self._fake_bdms()

        # Make sure power on fails.
        mock_pwron.side_effect = exc.Forbidden()

        # Invoke the method.
        self.assertRaises(exc.Forbidden, self.drv.spawn, 'context', inst,
                          mock.Mock(), 'injected_files', 'admin_password',
                          block_device_info=block_device_info)

        # Create LPAR was called
        self.crt_lpar.assert_called_with(self.apt, self.drv.host_wrapper,
                                         inst, my_flavor)
        self.assertEqual(2, self.vol_drv.connect_volume.call_count)

        # Power on was called
        self.assertTrue(mock_pwron.called)
        self.assertFalse(mock_pwron.call_args[1]['synchronous'])

        # Validate the rollbacks were called
        self.assertEqual(2, self.vol_drv.disconnect_volume.call_count)

    @mock.patch('nova.virt.block_device.DriverVolumeBlockDevice.save')
    @mock.patch('nova_powervm.virt.powervm.tasks.storage.CreateDiskForImg'
                '.execute')
    @mock.patch('nova_powervm.virt.powervm.driver.PowerVMDriver.'
                '_is_booted_from_volume')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugMgmtVif.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugVifs.execute')
    @mock.patch('nova.virt.configdrive.required_by')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    @mock.patch('nova_powervm.virt.powervm.tasks.vm.UpdateIBMiSettings'
                '.execute')
    @mock.patch('nova_powervm.virt.powervm.driver.PowerVMDriver.'
                '_get_boot_connectivity_type')
    @mock.patch('pypowervm.tasks.power.power_on')
    def test_spawn_ibmi(
        self, mock_pwron, mock_boot_conn_type,
        mock_update_lod_src, mock_get_flv, mock_cfg_drv,
        mock_plug_vifs, mock_plug_mgmt_vif, mock_boot_from_vol,
        mock_crt_img, mock_save):
        """Validates the PowerVM spawn to create an IBMi server.
        """
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.system_metadata = {'image_os_distro': 'ibmi'}
        my_flavor = inst.get_flavor()
        mock_get_flv.return_value = my_flavor
        mock_cfg_drv.return_value = False
        mock_boot_from_vol.return_value = True
        mock_boot_conn_type.return_value = 'vscsi'
        # Create some fake BDMs
        block_device_info = self._fake_bdms()
        image_meta = {}
        # Invoke the method.
        self.drv.spawn('context', inst, image_meta,
                       'injected_files', 'admin_password',
                       block_device_info=block_device_info)

        self.assertTrue(mock_boot_from_vol.called)
        # Since the root device is in the BDMs we do not expect the image disk
        # to be created.
        self.assertFalse(mock_crt_img.called)

        # Create LPAR was called
        self.crt_lpar.assert_called_with(self.apt, self.drv.host_wrapper,
                                         inst, my_flavor)

        self.assertTrue(mock_boot_conn_type.called)
        self.assertTrue(mock_update_lod_src.called)

        # Power on was called
        self.assertTrue(mock_pwron.called)
        self.assertFalse(mock_pwron.call_args[1]['synchronous'])

        # Check that the connect volume was called
        self.assertEqual(2, self.vol_drv.connect_volume.call_count)

        # Make sure the BDM save was invoked twice.
        self.assertEqual(2, mock_save.call_count)

    @mock.patch('nova_powervm.virt.powervm.tasks.storage.'
                'CreateAndConnectCfgDrive.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.storage.ConnectVolume'
                '.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.storage.CreateDiskForImg'
                '.execute')
    @mock.patch('nova_powervm.virt.powervm.driver.PowerVMDriver.'
                '_is_booted_from_volume')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugMgmtVif.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugVifs.execute')
    @mock.patch('nova.virt.configdrive.required_by')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    @mock.patch('nova_powervm.virt.powervm.tasks.vm.UpdateIBMiSettings'
                '.execute')
    @mock.patch('nova_powervm.virt.powervm.driver.PowerVMDriver.'
                '_get_boot_connectivity_type')
    @mock.patch('pypowervm.tasks.power.power_on')
    def test_spawn_ibmi_without_bdms(
        self, mock_pwron, mock_boot_conn_type, mock_update_lod_src,
        mock_get_flv, mock_cfg_drv, mock_plug_vifs,
        mock_plug_mgmt_vif, mock_boot_from_vol, mock_crt_disk_img,
        mock_conn_vol, mock_crt_cfg_drv):
        """Validates the 'typical' spawn flow for IBMi
        Perform an UT using an image with local disk, attaching networks
        and powering on.
        """
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.system_metadata = {'image_os_distro': 'ibmi'}
        my_flavor = inst.get_flavor()
        mock_get_flv.return_value = my_flavor
        mock_cfg_drv.return_value = False
        mock_boot_from_vol.return_value = False
        mock_boot_conn_type.return_value = 'vscsi'
        # Invoke the method.
        self.drv.spawn('context', inst, mock.Mock(),
                       'injected_files', 'admin_password')

        # Assert the correct tasks were called
        self.assertTrue(mock_plug_vifs.called)
        self.assertTrue(mock_plug_mgmt_vif.called)
        self.assertTrue(mock_crt_disk_img.called)
        self.crt_lpar.assert_called_with(
            self.apt, self.drv.host_wrapper, inst, my_flavor)
        self.assertTrue(mock_update_lod_src.called)
        self.assertTrue(mock_pwron.called)
        self.assertFalse(mock_pwron.call_args[1]['synchronous'])
        # Assert that tasks that are not supposed to be called are not called
        self.assertFalse(mock_conn_vol.called)
        self.assertFalse(mock_crt_cfg_drv.called)

    @mock.patch('nova_powervm.virt.powervm.disk.localdisk.LocalStorage.'
                'delete_disks')
    @mock.patch('nova_powervm.virt.powervm.tasks.storage.CreateDiskForImg.'
                'execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugMgmtVif.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugVifs.execute')
    @mock.patch('nova_powervm.virt.powervm.vm.dlt_lpar')
    @mock.patch('nova.virt.configdrive.required_by')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    def test_spawn_ops_rollback_disk(
        self, mock_get_flv, mock_cfg_drv, mock_dlt, mock_plug_vifs,
        mock_plug_mgmt_vifs, mock_crt_disk, mock_delete_disks):
        """Validates the rollback if failure occurs on disk create."""
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.system_metadata = {'image_os_distro': 'rhel'}
        my_flavor = inst.get_flavor()
        mock_get_flv.return_value = my_flavor
        mock_cfg_drv.return_value = False

        # Make sure power on fails.
        mock_crt_disk.side_effect = exc.Forbidden()

        # Invoke the method.
        self.assertRaises(exc.Forbidden, self.drv.spawn, 'context', inst,
                          mock.Mock(), 'injected_files', 'admin_password',
                          block_device_info=None)

        # Create LPAR was called
        self.crt_lpar.assert_called_with(self.apt, self.drv.host_wrapper,
                                         inst, my_flavor)

        # Since the create disks method failed, the delete disks should not
        # have been called
        self.assertFalse(mock_delete_disks.called)

    @mock.patch('nova.virt.block_device.DriverVolumeBlockDevice.save')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugMgmtVif.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.network.PlugVifs.execute')
    @mock.patch('nova_powervm.virt.powervm.vm.dlt_lpar')
    @mock.patch('nova.virt.configdrive.required_by')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    @mock.patch('pypowervm.tasks.power.power_on')
    @mock.patch('pypowervm.tasks.power.power_off')
    def test_spawn_ops_rollback_on_vol_connect(
        self, mock_pwroff, mock_pwron, mock_get_flv, mock_cfg_drv, mock_dlt,
        mock_plug_vifs, mock_plug_mgmt_vifs, mock_save):
        """Validates the rollbacks on a volume connect failure."""
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.system_metadata = {'image_os_distro': 'rhel'}
        my_flavor = inst.get_flavor()
        mock_get_flv.return_value = my_flavor
        mock_cfg_drv.return_value = False
        block_device_info = self._fake_bdms()

        # Have the connect fail.  Also fail the disconnect on revert.  Should
        # not block the rollback.
        self.vol_drv.connect_volume.side_effect = exc.Forbidden()
        self.vol_drv.disconnect_volume.side_effect = p_exc.VolumeDetachFailed(
            volume_id='1', instance_name=inst.name, reason='Test Case')

        # Invoke the method.
        self.assertRaises(exc.Forbidden, self.drv.spawn, 'context', inst,
                          mock.Mock(), 'injected_files', 'admin_password',
                          block_device_info=block_device_info)

        # Create LPAR was called
        self.crt_lpar.assert_called_with(self.apt, self.drv.host_wrapper,
                                         inst, my_flavor)
        self.assertEqual(1, self.vol_drv.connect_volume.call_count)

        # Power on should not be called.  Shouldn't get that far in flow.
        self.assertFalse(mock_pwron.called)

        # Disconnect should, as it may need to remove from one of the VIOSes
        # (but maybe failed on another).
        self.assertTrue(self.vol_drv.disconnect_volume.called)

    @mock.patch('nova.block_device.get_root_bdm')
    @mock.patch('nova.virt.driver.block_device_info_get_mapping')
    def test_is_booted_from_volume(self, mock_get_mapping, mock_get_root_bdm):
        block_device_info = self._fake_bdms()
        ret = self.drv._is_booted_from_volume(block_device_info)
        mock_get_root_bdm.\
            assert_called_once_with(mock_get_mapping.return_value)
        self.assertTrue(ret)
        self.assertEqual(1, mock_get_mapping.call_count)

        mock_get_mapping.reset_mock()
        mock_get_root_bdm.return_value = None
        ret = self.drv._is_booted_from_volume(block_device_info)
        self.assertFalse(ret)
        self.assertEqual(1, mock_get_mapping.call_count)

    def test_get_inst_xag(self):
        # No volumes - should be just the SCSI mapping
        xag = self.drv._get_inst_xag(mock.Mock(), None)
        self.assertEqual([pvm_vios.VIOS.xags.SCSI_MAPPING], xag)

        # The vSCSI Volume attach - only needs the SCSI mapping.
        self.flags(fc_attach_strategy='vscsi', group='powervm')
        xag = self.drv._get_inst_xag(mock.Mock(), [mock.Mock()])
        self.assertEqual([pvm_vios.VIOS.xags.SCSI_MAPPING], xag)

        # The NPIV volume attach - requires SCSI, Storage and FC Mapping
        self.flags(fc_attach_strategy='npiv', group='powervm')
        xag = self.drv._get_inst_xag(mock.Mock(), [mock.Mock()])
        self.assertEqual(set([pvm_vios.VIOS.xags.STORAGE,
                              pvm_vios.VIOS.xags.SCSI_MAPPING,
                              pvm_vios.VIOS.xags.FC_MAPPING]), set(xag))

    @mock.patch('nova_powervm.virt.powervm.driver.PowerVMDriver.'
                '_is_booted_from_volume')
    @mock.patch('nova_powervm.virt.powervm.vm.dlt_lpar')
    @mock.patch('nova_powervm.virt.powervm.vm.power_off')
    @mock.patch('nova_powervm.virt.powervm.media.ConfigDrivePowerVM.'
                'dlt_vopt')
    @mock.patch('nova_powervm.virt.powervm.media.ConfigDrivePowerVM.'
                '_validate_vopt_vg')
    @mock.patch('nova_powervm.virt.powervm.vm.get_pvm_uuid')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    def test_destroy(
        self, mock_get_flv, mock_pvmuuid, mock_val_vopt, mock_dlt_vopt,
        mock_pwroff, mock_dlt, mock_boot_from_vol):
        """Validates the basic PowerVM destroy."""
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.task_state = None

        # BDMs
        mock_bdms = self._fake_bdms()
        mock_boot_from_vol.return_value = False
        # Invoke the method.
        self.drv.destroy('context', inst, mock.Mock(),
                         block_device_info=mock_bdms)

        # Power off was called
        self.assertTrue(mock_pwroff.called)

        # Validate that the vopt delete was called
        self.assertTrue(mock_dlt_vopt.called)

        # Validate that the volume detach was called
        self.assertEqual(2, self.vol_drv.disconnect_volume.call_count)
        # Delete LPAR was called
        mock_dlt.assert_called_with(self.apt, mock.ANY)

        # Validate root device in bdm was checked.
        mock_boot_from_vol.assert_called_with(mock_bdms)

        # Validate disk driver detach and delete disk methods were called.
        self.assertTrue(self.drv.disk_dvr.delete_disks.called)
        self.assertTrue(self.drv.disk_dvr.disconnect_image_disk.called)

        def reset_mocks():
            # Reset the mocks
            for mk in [mock_pwroff, mock_dlt, mock_dlt_vopt,
                       self.vol_drv, mock_dlt,
                       mock_boot_from_vol]:
                mk.reset_mock()

        def assert_not_called():
            # Power off was not called
            self.assertFalse(mock_pwroff.called)

            # Validate that the vopt delete was not called
            self.assertFalse(mock_dlt_vopt.called)

            # Validate that the volume detach was not called
            self.assertFalse(self.vol_drv.disconnect_volume.called)

            # Delete LPAR was not called
            self.assertFalse(mock_dlt.called)

        # Test when the VM's root device is a BDM.
        reset_mocks()
        mock_boot_from_vol.return_value = True
        self.drv.disk_dvr.delete_disks.reset_mock()
        self.drv.disk_dvr.disconnect_image_disk.reset_mock()

        # Invoke the method.
        self.drv.destroy('context', inst, mock.Mock(),
                         block_device_info=mock_bdms)

        # Validate root device in bdm was checked.
        mock_boot_from_vol.assert_called_with(mock_bdms)

        # Validate disk driver detach and delete disk methods were called.
        self.assertFalse(self.drv.disk_dvr.delete_disks.called)
        self.assertFalse(self.drv.disk_dvr.disconnect_image_disk.called)

        # Start negative tests
        reset_mocks()
        # Pretend we didn't find the VM on the system
        mock_pvmuuid.side_effect = exc.InstanceNotFound(instance_id=inst.name)

        # Invoke the method.
        self.drv.destroy('context', inst, mock.Mock(),
                         block_device_info=mock_bdms)
        assert_not_called()

        mock_resp = mock.Mock()
        mock_resp.status = 404
        mock_resp.reqpath = (
            '/rest/api/uom/ManagedSystem/c5d782c7-44e4-3086-ad15-'
            'b16fb039d63b/LogicalPartition/1B5FB633-16D1-4E10-A14'
            '5-E6FB905161A3?group=None')
        mock_pvmuuid.side_effect = pvm_exc.HttpError(mock_resp)
        # Invoke the method.
        self.drv.destroy('context', inst, mock.Mock(),
                         block_device_info=mock_bdms)
        assert_not_called()

        # Ensure the exception is raised with non-matching path
        reset_mocks()
        mock_resp.reqpath = (
            '/rest/api/uom/ManagedSystem/c5d782c7-44e4-3086-ad15-'
            'b16fb039d63b/SomeResource/1B5FB633-16D1-4E10-A14'
            '5-E6FB905161A3?group=None')
        # Invoke the method.
        self.assertRaises(pvm_exc.HttpError, self.drv.destroy, 'context', inst,
                          mock.Mock(), block_device_info=mock_bdms)
        assert_not_called()

    def test_attach_volume(self):
        """Validates the basic PowerVM attach volume."""
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.task_state = None
        inst.save = mock.Mock()

        # BDMs
        mock_bdm = self._fake_bdms()['block_device_mapping'][0]

        # Invoke the method.
        self.drv.attach_volume('context', mock_bdm.get('connection_info'),
                               inst, mock.Mock())

        # Verify the connect volume was invoked
        self.assertEqual(1, self.vol_drv.connect_volume.call_count)
        self.assertTrue(inst.save.called)

    @mock.patch('nova_powervm.virt.powervm.vm.instance_exists')
    def test_detach_volume(self, mock_inst_exists):
        """Validates the basic PowerVM detach volume."""
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.task_state = None

        # Mock that the instance exists for the first test, then not.
        mock_inst_exists.side_effect = [True, False, False]

        # BDMs
        mock_bdm = self._fake_bdms()['block_device_mapping'][0]
        # Invoke the method, good path test.
        self.drv.detach_volume(mock_bdm.get('connection_info'), inst,
                               mock.Mock())

        # Verify the disconnect volume was invoked
        self.assertEqual(1, self.vol_drv.disconnect_volume.call_count)

        # Invoke the method, instance doesn't exist, no migration
        self.vol_drv.disconnect_volume.reset_mock()
        self.drv.detach_volume(mock_bdm.get('connection_info'), inst,
                               mock.Mock())
        # Verify the disconnect volume was not invoked
        self.assertEqual(0, self.vol_drv.disconnect_volume.call_count)

        # Test instance doesn't exist, migration cleanup
        self.vol_drv.disconnect_volume.reset_mock()
        mig = lpm.LiveMigrationDest(self.drv, inst)
        self.drv.live_migrations[inst.uuid] = mig
        with mock.patch.object(mig, 'cleanup_volume') as mock_clnup:
            self.drv.detach_volume(mock_bdm.get('connection_info'), inst,
                                   mock.Mock())
        # The cleanup should have been called since there was a migration
        self.assertEqual(1, mock_clnup.call_count)
        # Verify the disconnect volume was not invoked
        self.assertEqual(0, self.vol_drv.disconnect_volume.call_count)

    @mock.patch('nova_powervm.virt.powervm.vm.dlt_lpar')
    @mock.patch('nova_powervm.virt.powervm.vm.power_off')
    @mock.patch('nova_powervm.virt.powervm.media.ConfigDrivePowerVM.'
                'dlt_vopt')
    @mock.patch('nova_powervm.virt.powervm.media.ConfigDrivePowerVM.'
                '_validate_vopt_vg')
    @mock.patch('nova.objects.flavor.Flavor.get_by_id')
    def test_destroy_rollback(
        self, mock_get_flv, mock_val_vopt, mock_dlt_vopt, mock_pwroff,
        mock_dlt):
        """Validates the basic PowerVM destroy rollback mechanism works."""
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        inst.task_state = None
        mock_get_flv.return_value = inst.get_flavor()

        # BDMs
        mock_bdms = self._fake_bdms()

        # Fire a failure in the power off.
        mock_dlt.side_effect = exc.Forbidden()

        # Have the connect volume fail on the rollback.  Should not block the
        # full rollback.
        self.vol_drv.connect_volume.side_effect = p_exc.VolumeAttachFailed(
            volume_id='1', instance_name=inst.name, reason='Test Case')

        # Invoke the method.
        self.assertRaises(exc.Forbidden, self.drv.destroy, 'context', inst,
                          mock.Mock(), block_device_info=mock_bdms)

        # Validate that the vopt delete was called
        self.assertTrue(mock_dlt_vopt.called)

        # Validate that the volume detach was called
        self.assertEqual(2, self.vol_drv.disconnect_volume.call_count)

        # Delete LPAR was called
        mock_dlt.assert_called_with(self.apt, mock.ANY)

        # Validate the rollbacks were called.
        self.assertEqual(2, self.vol_drv.connect_volume.call_count)

    @mock.patch('nova_powervm.virt.powervm.vm.power_off')
    @mock.patch('nova_powervm.virt.powervm.vm.update')
    def test_resize(self, mock_update, mock_pwr_off):
        """Validates the PowerVM driver resize operation."""
        # Set up the mocks to the resize operation.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        host = self.drv.get_host_ip_addr()
        resp = pvm_adp.Response('method', 'path', 'status', 'reason', {})
        resp.entry = pvm_lpar.LPAR._bld(None).entry
        self.apt.read.return_value = resp

        # BDMs
        mock_bdms = self._fake_bdms()

        # Catch root disk resize smaller.
        small_root = objects.Flavor(vcpus=1, memory_mb=2048, root_gb=9)
        self.assertRaises(
            exc.InstanceFaultRollback, self.drv.migrate_disk_and_power_off,
            'context', inst, 'dest', small_root, 'network_info', mock_bdms)

        new_flav = objects.Flavor(vcpus=1, memory_mb=2048, root_gb=10)

        # We don't support resize to different host.
        self.assertRaises(
            NotImplementedError, self.drv.migrate_disk_and_power_off,
            'context', inst, 'bogus host', new_flav, 'network_info', mock_bdms)

        self.drv.migrate_disk_and_power_off(
            'context', inst, host, new_flav, 'network_info', mock_bdms)
        mock_pwr_off.assert_called_with(
            self.drv.adapter, inst, self.drv.host_uuid, entry=mock.ANY)
        mock_update.assert_called_with(
            self.drv.adapter, self.drv.host_wrapper, inst, new_flav,
            entry=mock.ANY)

        # Boot disk resize
        boot_flav = objects.Flavor(vcpus=1, memory_mb=2048, root_gb=12)
        self.drv.migrate_disk_and_power_off(
            'context', inst, host, boot_flav, 'network_info', mock_bdms)
        self.drv.disk_dvr.extend_disk.assert_called_with(
            'context', inst, dict(type='boot'), 12)

    @mock.patch('nova_powervm.virt.powervm.driver.vm')
    @mock.patch('nova_powervm.virt.powervm.tasks.vm.vm')
    @mock.patch('nova_powervm.virt.powervm.tasks.vm.power')
    def test_rescue(self, mock_task_pwr, mock_task_vm, mock_dvr_vm):
        """Validates the PowerVM driver rescue operation."""
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        self.drv.disk_dvr = mock.Mock()

        # Invoke the method.
        self.drv.rescue('context', inst, mock.MagicMock(),
                        mock.MagicMock(), 'rescue_psswd')

        self.assertTrue(mock_task_vm.power_off.called)
        self.assertTrue(self.drv.disk_dvr.create_disk_from_image.called)
        self.assertTrue(self.drv.disk_dvr.connect_disk.called)
        self.assertTrue(mock_task_pwr.power_on.called)
        self.assertFalse(mock_task_pwr.power_on.call_args[1]['synchronous'])

    @mock.patch('nova_powervm.virt.powervm.driver.vm')
    @mock.patch('nova_powervm.virt.powervm.tasks.vm.vm')
    @mock.patch('nova_powervm.virt.powervm.tasks.vm.power')
    def test_unrescue(self, mock_task_pwr, mock_task_vm, mock_dvr_vm):
        """Validates the PowerVM driver rescue operation."""
        # Set up the mocks to the tasks.
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        self.drv.disk_dvr = mock.Mock()

        # Invoke the method.
        self.drv.unrescue(inst, 'network_info')

        self.assertTrue(mock_task_vm.power_off.called)
        self.assertTrue(self.drv.disk_dvr.disconnect_image_disk.called)
        self.assertTrue(self.drv.disk_dvr.delete_disks.called)
        self.assertTrue(mock_task_pwr.power_on.called)
        self.assertFalse(mock_task_pwr.power_on.call_args[1]['synchronous'])

    @mock.patch('nova_powervm.virt.powervm.driver.LOG')
    def test_log_op(self, mock_log):
        """Validates the log_operations."""
        drv = driver.PowerVMDriver(fake.FakeVirtAPI())
        inst = objects.Instance(**powervm.TEST_INSTANCE)

        drv._log_operation('fake_op', inst)
        entry = (r'Operation: %(op)s. Virtual machine display '
                 'name: %(display_name)s, name: %(name)s, '
                 'UUID: %(uuid)s')
        msg_dict = {'uuid': '49629a5c-f4c4-4721-9511-9725786ff2e5',
                    'display_name': u'Fake Instance',
                    'name': 'instance-00000001',
                    'op': 'fake_op'}
        mock_log.info.assert_called_with(entry, msg_dict)

    def test_host_resources(self):
        # Set the return value of None so we use the cached value in the drv
        self.apt.read.return_value = None
        self.drv.host_wrapper = self.wrapper

        stats = self.drv.get_available_resource('nodename')
        self.assertIsNotNone(stats)

        # Check for the presence of fields added to host stats
        fields = ('local_gb', 'local_gb_used')

        for fld in fields:
            value = stats.get(fld, None)
            self.assertIsNotNone(value)

    @mock.patch('pypowervm.wrappers.logical_partition.LPAR.can_modify_io')
    @mock.patch('nova_powervm.virt.powervm.vm.crt_secure_rmc_vif')
    @mock.patch('nova_powervm.virt.powervm.vm.get_secure_rmc_vswitch')
    @mock.patch('nova_powervm.virt.powervm.vm.crt_vif')
    @mock.patch('nova_powervm.virt.powervm.vm.get_cnas')
    def test_plug_vifs(
        self, mock_vm_get, mock_vm_crt, mock_get_rmc_vswitch, mock_crt_rmc_vif,
        mock_can_modify_io):
        inst = objects.Instance(**powervm.TEST_INSTANCE)

        # Mock up the CNA response
        cnas = [mock.MagicMock(), mock.MagicMock()]
        cnas[0].mac = 'AABBCCDDEEFF'
        cnas[0].vswitch_uri = 'fake_uri'
        cnas[1].mac = 'AABBCCDDEE11'
        cnas[1].vswitch_uri = 'fake_mgmt_uri'
        mock_vm_get.return_value = cnas

        mock_can_modify_io.return_value = True, None

        # Mock up the network info.  They get sanitized to upper case.
        net_info = [
            {'address': 'aa:bb:cc:dd:ee:ff'},
            {'address': 'aa:bb:cc:dd:ee:22'}
        ]

        # Mock up the rmc vswitch
        vswitch_w = mock.MagicMock()
        vswitch_w.href = 'fake_mgmt_uri'
        mock_get_rmc_vswitch.return_value = vswitch_w

        # Run method
        self.drv.plug_vifs(inst, net_info)

        # The create should have only been called once.  The other was already
        # existing.
        self.assertEqual(1, mock_vm_crt.call_count)
        self.assertEqual(0, mock_crt_rmc_vif.call_count)

    @mock.patch('nova_powervm.virt.powervm.tasks.vm.Get')
    def test_plug_vif_failures(self, mock_vm):
        inst = objects.Instance(**powervm.TEST_INSTANCE)

        # Test instance not found handling
        mock_vm.execute.side_effect = exc.InstanceNotFound(
            instance_id=inst)

        # Run method
        self.assertRaises(exc.VirtualInterfacePlugException,
                          self.drv.plug_vifs, inst, {})

        # Test a random Exception
        mock_vm.execute.side_effect = ValueError()

        # Run method
        self.assertRaises(exc.VirtualInterfacePlugException,
                          self.drv.plug_vifs, inst, {})

    @mock.patch('nova_powervm.virt.powervm.tasks.vm.Get')
    def test_unplug_vif_failures(self, mock_vm):
        inst = objects.Instance(**powervm.TEST_INSTANCE)

        # Test instance not found handling
        mock_vm.execute.side_effect = exc.InstanceNotFound(
            instance_id=inst)

        # Run method
        self.assertRaises(exc.InterfaceDetachFailed,
                          self.drv.unplug_vifs, inst, {})

    def test_extract_bdm(self):
        """Tests the _extract_bdm method."""
        self.assertEqual([], self.drv._extract_bdm(None))
        self.assertEqual([], self.drv._extract_bdm({'fake': 'val'}))

        fake_bdi = {'block_device_mapping': ['content']}
        self.assertListEqual(['content'], self.drv._extract_bdm(fake_bdi))

    def test_inst_dict(self):
        """Tests the _inst_dict method."""
        class_name = 'nova_powervm.tests.virt.powervm.test_driver.FakeClass'
        inst_dict = driver._inst_dict({'test': class_name})

        self.assertEqual(1, len(inst_dict.keys()))
        self.assertIsInstance(inst_dict['test'], FakeClass)

    def test_get_host_ip_addr(self):
        self.assertEqual(self.drv.get_host_ip_addr(), CONF.my_ip)

    @mock.patch('nova_powervm.virt.powervm.driver.LOG.warn')
    @mock.patch('nova.compute.utils.get_machine_ips')
    def test_get_host_ip_addr_failure(self, mock_ips, mock_log):
        mock_ips.return_value = ['1.1.1.1']
        self.drv.get_host_ip_addr()
        mock_log.assert_called_once_with(u'my_ip address (%(my_ip)s) was '
                                         u'not found on any of the '
                                         u'interfaces: %(ifaces)s',
                                         {'ifaces': '1.1.1.1',
                                          'my_ip': mock.ANY})

    def test_shared_stg_calls(self):
        data = self.drv.check_instance_shared_storage_local('context', 'inst')
        self.assertTrue(
            self.drv.disk_dvr.check_instance_shared_storage_local.called)

        self.drv.check_instance_shared_storage_remote('context', data)
        self.assertTrue(
            self.drv.disk_dvr.check_instance_shared_storage_remote.called)

        self.drv.check_instance_shared_storage_cleanup('context', data)
        self.assertTrue(
            self.drv.disk_dvr.check_instance_shared_storage_cleanup.called)

    @mock.patch('pypowervm.tasks.power.power_on')
    @mock.patch('pypowervm.tasks.power.power_off')
    def test_reboot(self, mock_pwroff, mock_pwron):
        entry = mock.Mock()
        self.get_inst_wrap.return_value = entry
        inst = objects.Instance(**powervm.TEST_INSTANCE)

        # VM is in 'not activated' state
        # Validate SOFT vs HARD and power_on called with each.
        entry.state = pvm_bp.LPARState.NOT_ACTIVATED
        self.assertTrue(self.drv.reboot('context', inst, None, 'SOFT'))
        # Make sure power off is not called
        self.assertEqual(0, mock_pwroff.call_count)
        mock_pwron.assert_called_with(entry, self.drv.host_uuid)
        self.assertTrue(self.drv.reboot('context', inst, None, 'HARD'))
        # Make sure power off is not called
        self.assertEqual(0, mock_pwroff.call_count)
        self.assertEqual(2, mock_pwron.call_count)
        mock_pwron.assert_called_with(entry, self.drv.host_uuid)

        # VM is not in 'not activated' state
        # reset mock_pwron
        mock_pwron.reset_mock()
        entry.state = 'whatever'
        self.assertTrue(self.drv.reboot('context', inst, None, 'SOFT'))
        mock_pwroff.assert_called_with(entry, self.drv.host_uuid,
                                       restart=True,
                                       force_immediate=False)
        self.assertEqual(0, mock_pwron.call_count)
        self.assertTrue(self.drv.reboot('context', inst, None, 'HARD'))
        mock_pwroff.assert_called_with(entry, self.drv.host_uuid,
                                       restart=True,
                                       force_immediate=True)
        self.assertEqual(0, mock_pwron.call_count)

        # If power_off raises an exception, power_on is not called, and the
        # exception percolates up.
        entry.state = 'whatever'
        mock_pwroff.side_effect = pvm_exc.VMPowerOffFailure(lpar_nm='lpar',
                                                            reason='reason')
        self.assertRaises(pvm_exc.VMPowerOffFailure, self.drv.reboot,
                          'context', inst, None, 'HARD')

        # If power_on raises an exception, it percolates up.
        entry.state = pvm_bp.LPARState.NOT_ACTIVATED
        mock_pwron.side_effect = pvm_exc.VMPowerOnFailure(lpar_nm='lpar',
                                                          reason='reason')
        self.assertRaises(pvm_exc.VMPowerOnFailure, self.drv.reboot, 'context',
                          inst, None, 'SOFT')

    @mock.patch('pypowervm.tasks.vterm.open_localhost_vnc_vterm')
    @mock.patch('nova_powervm.virt.powervm.vm.get_pvm_uuid')
    def test_get_vnc_console(self, mock_uuid, mock_vterm):
        # Mock response
        mock_vterm.return_value = '10'

        # Invoke
        inst = objects.Instance(**powervm.TEST_INSTANCE)
        resp = self.drv.get_vnc_console(mock.ANY, inst)

        # Validate
        self.assertEqual('127.0.0.1', resp.host)
        self.assertEqual('10', resp.port)

    @staticmethod
    def _fake_bdms():
        def _fake_bdm(volume_id, target_lun):
            connection_info = {'driver_volume_type': 'fibre_channel',
                               'data': {'volume_id': volume_id,
                                        'target_lun': target_lun,
                                        'initiator_target_map':
                                        {'21000024F5': ['50050768']}}}
            mapping_dict = {'source_type': 'volume', 'volume_id': volume_id,
                            'destination_type': 'volume',
                            'connection_info':
                                jsonutils.dumps(connection_info),
                            }
            bdm_dict = nova_block_device.BlockDeviceDict(mapping_dict)
            bdm_obj = bdmobj.BlockDeviceMapping(**bdm_dict)

            return nova_virt_bdm.DriverVolumeBlockDevice(bdm_obj)

        bdm_list = [_fake_bdm('fake_vol1', 0), _fake_bdm('fake_vol2', 1)]
        block_device_info = {'block_device_mapping': bdm_list}

        return block_device_info

    @mock.patch('nova_powervm.virt.powervm.tasks.image.UpdateTaskState.'
                'execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.storage.InstanceDiskToMgmt.'
                'execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.image.StreamToGlance.execute')
    @mock.patch('nova_powervm.virt.powervm.tasks.storage.'
                'RemoveInstanceDiskFromMgmt.execute')
    def test_snapshot(self, mock_rm, mock_stream, mock_conn, mock_update):
        inst = mock.Mock()
        inst.display_name = 'inst'
        mock_conn.return_value = 'stg_elem', 'vios_wrap', 'disk_path'
        self.drv.snapshot('context', inst, 'image_id', 'update_task_state')
        self.assertEqual(2, mock_update.call_count)
        self.assertEqual(1, mock_conn.call_count)
        mock_stream.assert_called_with(disk_path='disk_path')
        mock_rm.assert_called_with(stg_elem='stg_elem', vios_wrap='vios_wrap',
                                   disk_path='disk_path')

    @mock.patch('nova_powervm.virt.powervm.live_migration.LiveMigrationDest')
    def test_can_migrate_dest(self, mock_lpm):
        mock_lpm.return_value.check_destination.return_value = 'dest_data'
        dest_data = self.drv.check_can_live_migrate_destination(
            'context', mock.Mock(), 'src_compute_info', 'dst_compute_info')
        self.assertEqual('dest_data', dest_data)

    def test_can_live_mig_dest_clnup(self):
        self.drv.check_can_live_migrate_destination_cleanup(
            'context', 'dest_data')

    @mock.patch('nova_powervm.virt.powervm.live_migration.LiveMigrationSrc')
    def test_can_live_mig_src(self, mock_lpm):
        mock_lpm.return_value.check_source.return_value = (
            'src_data')
        src_data = self.drv.check_can_live_migrate_source(
            'context', mock.Mock(), 'dest_check_data')
        self.assertEqual('src_data', src_data)

    def test_pre_live_migr(self):
        block_device_info = self._fake_bdms()
        resp = self.drv.pre_live_migration(
            'context', self.lpm_inst, block_device_info, 'network_info',
            'disk_info', migrate_data='migrate_data')
        self.assertIsNotNone(resp)

    def test_live_migration(self):
        mock_post_meth = mock.Mock()
        mock_rec_meth = mock.Mock()

        # Good path
        self.drv.live_migration(
            'context', self.lpm_inst, 'dest', mock_post_meth, mock_rec_meth,
            'block_mig', 'migrate_data')

        mock_post_meth.assert_called_once_with(
            'context', self.lpm_inst, 'dest', mock.ANY, mock.ANY)
        self.assertEqual(0, mock_rec_meth.call_count)

        # Abort invocation path
        self._setup_lpm()
        mock_post_meth.reset_mock()
        mock_kwargs = {'operation_name': 'op', 'seconds': 10}
        self.lpm.live_migration.side_effect = (
            pvm_exc.JobRequestTimedOut(**mock_kwargs))
        self.assertRaises(
            lpm.LiveMigrationFailed, self.drv.live_migration,
            'context', self.lpm_inst, 'dest', mock_post_meth, mock_rec_meth,
            'block_mig', 'migrate_data')
        self.lpm.migration_abort.assert_called_once_with()
        mock_rec_meth.assert_called_once_with(
            'context', self.lpm_inst, 'dest', mock.ANY, mock.ANY)
        self.lpm.rollback_live_migration.assert_called_once_with('context')
        self.assertEqual(0, mock_post_meth.call_count)

        # Exception path
        self._setup_lpm()
        mock_post_meth.reset_mock()
        mock_rec_meth.reset_mock()
        self.lpm.live_migration.side_effect = ValueError()
        self.assertRaises(
            lpm.LiveMigrationFailed, self.drv.live_migration,
            'context', self.lpm_inst, 'dest', mock_post_meth, mock_rec_meth,
            'block_mig', 'migrate_data')
        mock_rec_meth.assert_called_once_with(
            'context', self.lpm_inst, 'dest', mock.ANY, mock.ANY)
        self.lpm.rollback_live_migration.assert_called_once_with('context')
        self.assertEqual(0, mock_post_meth.call_count)

        # Ensure we get LiveMigrationFailed even if recovery fails.
        self._setup_lpm()
        mock_post_meth.reset_mock()
        mock_rec_meth.reset_mock()
        self.lpm.live_migration.side_effect = ValueError()
        # Cause the recovery method to fail with an exception.
        mock_rec_meth.side_effect = ValueError()
        self.assertRaises(
            lpm.LiveMigrationFailed, self.drv.live_migration,
            'context', self.lpm_inst, 'dest', mock_post_meth, mock_rec_meth,
            'block_mig', 'migrate_data')
        mock_rec_meth.assert_called_once_with(
            'context', self.lpm_inst, 'dest', mock.ANY, mock.ANY)
        self.lpm.rollback_live_migration.assert_called_once_with('context')
        self.assertEqual(0, mock_post_meth.call_count)

    def test_rollbk_lpm_dest(self):
        self.drv.rollback_live_migration_at_destination(
            'context', self.lpm_inst, 'network_info', 'block_device_info')
        self.assertRaises(
            KeyError, lambda: self.drv.live_migrations[self.lpm_inst.uuid])

    def test_post_live_mig(self):
        self.drv.post_live_migration('context', self.lpm_inst, None)
        self.lpm.post_live_migration.assert_called_once_with([], None)

    def test_post_live_mig_src(self):
        self.drv.post_live_migration_at_source('context', self.lpm_inst,
                                               'network_info')
        self.lpm.post_live_migration_at_source.assert_called_once_with(
            'network_info')

    def test_post_live_mig_dest(self):
        self.drv.post_live_migration_at_destination(
            'context', self.lpm_inst, 'network_info')
        self.lpm.post_live_migration_at_destination.assert_called_once_with(
            'network_info', [])
