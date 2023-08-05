from nose.tools import (
    assert_equal, assert_raises, assert_true, assert_almost_equal,
    assert_is_none)

# handle py3 and py2 cases:
try:
    import unittest.mock as mock
except ImportError:
    import mock

patch = mock.patch

import python_kemptech_api.client as client
from python_kemptech_api.client import LoadMaster
import python_kemptech_api.exceptions as exceptions
from python_kemptech_api.client import VirtualService


class Test_VirtualService:
    def setup(self):
        self.lm_info = {
            "endpoint": "https://bal:2fourall@1.1.1.1:443/access",
            "ip_address": "1.1.1.1",
        }
        self.vs = VirtualService(self.lm_info, "1.1.1.2")

    def test_init_throws_key_error(self):
        lm_info_with_no_endpoint = {"ip_address": "1.1.1.1"}
        lm_info_with_no_ip_address = {"endpoint": "https://bal:2fourall@1.1.1.1:443/access"}
        VirtualService(self.lm_info, "1.1.1.2")
        with assert_raises(exceptions.VirtualServiceMissingLoadmasterInfo):
            VirtualService(lm_info_with_no_endpoint, "1.1.1.2")
        with assert_raises(exceptions.VirtualServiceMissingLoadmasterInfo):
            VirtualService(lm_info_with_no_ip_address, "1.1.1.2")

    def test_str(self):
        assert_equal(str(self.vs), "Virtual Service TCP 1.1.1.2:80 on "
                                   "LoadMaster 1.1.1.1")

    def test__get_base_parameters(self):
        base_params = self.vs._get_base_parameters()
        expected_params = {
            "vs": "1.1.1.2",
            "port": 80,
            "prot": "tcp",
        }
        assert_equal(base_params, expected_params)

    def test_to_api_dict(self):
        actual = self.vs.to_api_dict()
        expected = {
            "vs": "1.1.1.2",
            "port": 80,
            "prot": "tcp",
        }
        assert_equal(actual, expected)