# Copyright 2014 IBM Corp.
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

import mock

from networking_powervm.plugins.ibm.agent.powervm import exceptions as np_exc
from networking_powervm.plugins.ibm.agent.powervm import utils
from networking_powervm.tests.unit.plugins.ibm.powervm import base

from pypowervm import const as pvm_const
from pypowervm import exceptions as pvm_exc
from pypowervm.helpers import log_helper as pvm_log
from pypowervm.tests import test_fixtures as pvm_fx
from pypowervm.tests.test_utils import pvmhttp
from pypowervm.wrappers import network as pvm_net

NET_BR_FILE = 'fake_network_bridge.txt'
VM_FILE = 'fake_lpar_feed.txt'
CNA_FILE = 'fake_cna.txt'
VSW_FILE = 'fake_virtual_switch.txt'
VIOS_FILE = 'fake_vios_feed3.txt'


class UtilsTest(base.BasePVMTestCase):
    """Tests the utility functions for the Shared Ethernet Adapter Logic."""

    def setUp(self):
        super(UtilsTest, self).setUp()

        self.adpt = self.useFixture(
            pvm_fx.AdapterFx(traits=pvm_fx.LocalPVMTraits)).adpt

        def resp(file_name):
            return pvmhttp.load_pvm_resp(
                file_name, adapter=self.adpt).get_response()

        self.net_br_resp = resp(NET_BR_FILE)
        self.vm_feed_resp = resp(VM_FILE)
        self.cna_resp = resp(CNA_FILE)
        self.vswitch_resp = resp(VSW_FILE)
        self.vios_feed_resp = resp(VIOS_FILE)

    def _mock_feed(self, feed):
        """Helper method to make the mock adapter."""
        # Sets the feed to be the response on the adapter for a single read
        self.adpt.read.return_value = feed
        self.adpt.read_by_href.return_value = feed

    def __cna(self, mac):
        """Create a Client Network Adapter mock."""

        class FakeCNA(object):

            @property
            def slot(self):
                return 1

            @property
            def mac(self):
                return mac

            @property
            def pvid(self):
                return 1

        return FakeCNA()

    def test_find_cna_for_mac(self):
        cna1 = self.__cna("1234567890AB")
        cna2 = self.__cna("123456789012")

        self.assertEqual(cna1, utils.find_cna_for_mac("1234567890AB",
                                                      [cna1, cna2]))
        self.assertEqual(None, utils.find_cna_for_mac("9876543210AB",
                                                      [cna1, cna2]))

    def test_norm_mac(self):
        EXPECTED = "12:34:56:78:90:ab"
        self.assertEqual(EXPECTED, utils.norm_mac("12:34:56:78:90:ab"))
        self.assertEqual(EXPECTED, utils.norm_mac("1234567890ab"))
        self.assertEqual(EXPECTED, utils.norm_mac("12:34:56:78:90:AB"))
        self.assertEqual(EXPECTED, utils.norm_mac("1234567890AB"))

    def test_list_bridges(self):
        """Test that we can load the bridges in properly."""
        self._mock_feed(self.net_br_resp)

        # Assert that two are read in
        bridges = utils.list_bridges(self.adpt, 'host_uuid')
        self.assertEqual(2, len(bridges))
        self.assertTrue(isinstance(bridges[0], pvm_net.NetBridge))

    def test_list_vm_entries(self):
        """Validates that VMs can be iterated on properly."""
        self._mock_feed(self.vm_feed_resp)

        # List the VMs and make some assertions
        vm_list = utils._list_vm_entries(self.adpt, 'host_uuid')
        self.assertEqual(17, len(vm_list))
        for vm in vm_list:
            self.assertIsNotNone(vm.uuid)

    @mock.patch('pypowervm.adapter.Adapter.read')
    def test_get_vswitch_map(self, mock_read):
        self._mock_feed(self.vswitch_resp)
        resp = utils.get_vswitch_map(self.adpt, 'host_uuid')
        self.assertEqual('https://9.1.2.3:12443/rest/api/uom/ManagedSystem/'
                         'c5d782c7-44e4-3086-ad15-b16fb039d63b/VirtualSwitch/'
                         'e1a852cb-2be5-3a51-9147-43761bc3d720',
                         resp[0])
        mock_read.assert_called_once_with('ManagedSystem',
                                          child_type='VirtualSwitch',
                                          root_id='host_uuid')

    def test_find_nb_for_cna(self):
        self._mock_feed(self.vswitch_resp)

        nb_wraps = pvm_net.NetBridge.wrap(self.net_br_resp)

        mock_client_adpt = mock.MagicMock()
        mock_client_adpt.vswitch_uri = ('https://9.1.2.3:12443/rest/api/uom/'
                                        'ManagedSystem/'
                                        'c5d782c7-44e4-3086-ad15-b16fb039d63b/'
                                        'VirtualSwitch/'
                                        'e1a852cb-2be5-3a51-9147-43761bc3d720')

        vswitch_map = utils.get_vswitch_map(self.adpt, 'host_uuid')

        # Should have a proper URI, so it should match
        resp = utils.find_nb_for_cna(nb_wraps, mock_client_adpt, vswitch_map)
        self.assertIsNotNone(resp)

        # Should not match if we change the vswitch URI
        mock_client_adpt.vswitch_uri = "Fake"
        resp = utils.find_nb_for_cna(nb_wraps, mock_client_adpt, vswitch_map)
        self.assertIsNone(resp)

    @mock.patch('networking_powervm.plugins.ibm.agent.powervm.utils.'
                '_list_vm_entries')
    @mock.patch('pypowervm.wrappers.network.CNA.wrap')
    def test_list_cnas(self, mock_cna_wrap, mock_list_vms):
        """Validates that the CNA's can be iterated against."""
        self._mock_feed(self.cna_resp)

        # Override the VM Entries with a fake CNA
        class FakeVM(object):
            @property
            def uuid(self):
                return 'fake_uuid'
        vm = FakeVM()

        def list_vms(adapter, host_uuid):
            return [vm]

        mock_list_vms.side_effect = list_vms
        mock_cna_wrap.return_value = ['mocked']

        def read(*args, **kwargs):
            # Ensure we don't have the log helper in the adapter on the call.
            helpers = kwargs['helpers']
            if pvm_log.log_helper in helpers:
                self.fail()
            return mock.Mock()
        self.adpt.read = read

        # Get the CNAs and validate
        cnas = utils.list_cnas(self.adpt, 'host_uuid')
        self.assertEqual(1, len(cnas))

    @mock.patch('networking_powervm.plugins.ibm.agent.powervm.utils.'
                'list_bridges')
    def test_parse_sea_mappings(self, mock_list_br):
        nb_wraps = pvm_net.NetBridge.wrap(self.net_br_resp)
        mock_list_br.return_value = nb_wraps

        self._mock_feed(self.vios_feed_resp)
        resp = utils.parse_sea_mappings(self.adpt, 'host_uuid',
                                        'default:ent8:21-25D0A')

        self.assertEqual(1, len(resp.keys()))
        self.assertIn('default', resp)
        self.assertEqual('764f3423-04c5-3b96-95a3-4764065400bd',
                         resp['default'])

    @mock.patch('networking_powervm.plugins.ibm.agent.powervm.utils.'
                'list_bridges')
    def test_parse_sea_mappings_no_bridges(self, mock_list_br):
        mock_list_br.return_value = []
        self._mock_feed(self.vios_feed_resp)
        self.assertRaises(np_exc.NoNetworkBridges, utils.parse_sea_mappings,
                          self.adpt, 'host_uuid', '1:2:3')

    @mock.patch('networking_powervm.plugins.ibm.agent.powervm.utils.'
                'list_bridges')
    def test_parse_sea_mappings_no_mapping(self, mock_list_br):
        nb_wraps = pvm_net.NetBridge.wrap(self.net_br_resp)
        mock_list_br.return_value = nb_wraps

        self._mock_feed(self.vios_feed_resp)
        resp = utils.parse_sea_mappings(self.adpt, 'host_uuid',
                                        'default:ent8:21-25D0A')

        self.assertEqual({'default': '764f3423-04c5-3b96-95a3-4764065400bd'},
                         resp)

    @mock.patch('networking_powervm.plugins.ibm.agent.powervm.utils.'
                '_parse_empty_bridge_mapping')
    @mock.patch('networking_powervm.plugins.ibm.agent.powervm.utils.'
                'list_bridges')
    def test_parse_call_to_empty_bridge(self, mock_list_br, mock_empty):
        nb_wraps = pvm_net.NetBridge.wrap(self.net_br_resp)
        mock_list_br.return_value = nb_wraps

        self._mock_feed(self.vios_feed_resp)
        utils.parse_sea_mappings(self.adpt, 'host_uuid', '')

        # Make sure the _parse_empty_bridge_mapping method was called
        self.assertEqual(1, mock_empty.call_count)

    def test_parse_empty_bridge_mappings(self):
        self._mock_feed(self.vios_feed_resp)

        proper_wrap = mock.MagicMock()
        proper_wrap.uuid = '5'
        resp = utils._parse_empty_bridge_mapping([proper_wrap])

        self.assertEqual({'default': '5'}, resp)

        # Try the failure path
        self.assertRaises(np_exc.MultiBridgeNoMapping,
                          utils._parse_empty_bridge_mapping,
                          [proper_wrap, mock.Mock()])

    def test_update_cna_pvid(self):
        """Validates the update_cna_pvid method."""
        def build_mock():
            # Need to rebuild.  Since it returns itself a standard reset will
            # recurse infinitely.
            cna = mock.MagicMock()
            cna.refresh.return_value = cna
            return cna

        self._mock_feed(self.vios_feed_resp)

        # Attempt happy path
        cna = build_mock()
        utils.update_cna_pvid(cna, 5)
        self.assertEqual(5, cna.pvid)
        self.assertEqual(1, cna.update.call_count)

        # Raise an error 3 times and make sure it eventually re-raises the root
        # etag exception
        cna = build_mock()
        err_resp = mock.MagicMock()
        err_resp.status = pvm_const.HTTPStatus.ETAG_MISMATCH
        error = pvm_exc.HttpError(err_resp)

        cna.update.side_effect = [error, error, error]
        self.assertRaises(pvm_exc.HttpError, utils.update_cna_pvid, cna, 5)
        self.assertEqual(3, cna.update.call_count)
        self.assertEqual(2, cna.refresh.call_count)

        # Raise an error 2 times and then eventually works
        cna = build_mock()
        cna.update.side_effect = [error, error, None]
        utils.update_cna_pvid(cna, 5)
        self.assertEqual(3, cna.update.call_count)
        self.assertEqual(2, cna.refresh.call_count)

        # Immediate re-raise of different type of exception
        cna = build_mock()
        err_resp.status = pvm_const.HTTPStatus.UNAUTHORIZED
        cna.update.side_effect = pvm_exc.HttpError(err_resp)

        self.assertRaises(pvm_exc.HttpError, utils.update_cna_pvid, cna, 5)
        self.assertEqual(1, cna.update.call_count)
        self.assertEqual(0, cna.refresh.call_count)
