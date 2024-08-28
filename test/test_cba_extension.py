##############################################################################
# COPYRIGHT Ericsson AB 2013
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################


import unittest
from litp.extensions.core_extension import CoreExtension
from cba_extension.cba_extension import CBAExtension
from network_extension.network_extension import NetworkExtension
from litp.core.execution_manager import ExecutionManager
from litp.core.model_manager import ModelManager
from litp.core.plugin_manager import PluginManager
from litp.core.puppet_manager import PuppetManager
from cba_extension.cba_extension import (CmwClusterValidator,
                                         LsbRuntimeValidator)


class TestcbaExtension(unittest.TestCase):

    def setUp(self):
        self.ext = CBAExtension()
        self.model = ModelManager()
        self.puppet_manager = PuppetManager(self.model)
        self.plugin_manager = PluginManager(self.model)
        self.execution = ExecutionManager(self.model,
                                          self.puppet_manager,
                                          self.plugin_manager)
        core_ext = CoreExtension()
        network_ext = NetworkExtension()

        for ext in [core_ext, network_ext]:
            self.plugin_manager.add_property_types(ext.define_property_types())
            self.plugin_manager.add_item_types(ext.define_item_types())
            if ext == core_ext:
                self.plugin_manager.add_default_model()

    def test_property_types_registered(self):
        prop_types_expected = ['example_property_type', ]
        prop_types = [pt.property_type_id for pt in
                      self.ext.define_property_types()]
        #self.assertEquals(prop_types_expected, prop_types)

    def test_item_types_registered(self):
        item_types_expected = ['example-custom-item-type', ]
        item_types = [it.item_type_id for it in
                      self.ext.define_item_types()]
#        self.assertEquals(item_types_expected, item_types)

    def test_validator_duplicate(self):
        properties = {'tipc_networks':'hb1,hb1', "internal_network":"hb2"}
        errors = CmwClusterValidator().validate(properties)
        self.assertEquals('<tipc_networks - ValidationError - Cannot create more than one TIPC link for the same network>', str(errors))

    def test_validator_mgmt_net_has_commas(self):
        properties = {'tipc_networks':'hb1,hb2', "internal_network":"hb11,hb12"}
        errors = CmwClusterValidator().validate(properties)
        self.assertEquals('<internal_network - ValidationError - TIPC internal link should not be a list>', str(errors))

    def test_lsb_validator_status_interval_too_low(self):
        properties = {'status_interval':'9', "status_timeout":"10"}
        errors = LsbRuntimeValidator().validate(properties)
        self.assertEquals('<status_interval - ValidationError - The property \'status_interval\' must be an integer with value >= 10 and <= 3600>', str(errors))

    def test_lsb_validator_status_interval_not_integer(self):
        properties = {'status_interval':'9a', "status_timeout":"10"}
        errors = LsbRuntimeValidator().validate(properties)
        self.assertEquals('<status_interval - ValidationError - The property \'status_interval\' must be an integer with value >= 10 and <= 3600>', str(errors))

    def test_lsb_validator_status_timeout_too_low(self):
        properties = {'status_interval':'10', "status_timeout":"9"}
        errors = LsbRuntimeValidator().validate(properties)
        self.assertEquals('<status_timeout - ValidationError - The property \'status_timeout\' must be an integer with value >= 10 and <= 3600>', str(errors))

    def test_lsb_validator_status_timeout_not_integer(self):
        properties = {'status_interval':'10', "status_timeout":"9a"}
        errors = LsbRuntimeValidator().validate(properties)
        self.assertEquals('<status_timeout - ValidationError - The property \'status_timeout\' must be an integer with value >= 10 and <= 3600>', str(errors))


if __name__ == '__main__':
    unittest.main()
