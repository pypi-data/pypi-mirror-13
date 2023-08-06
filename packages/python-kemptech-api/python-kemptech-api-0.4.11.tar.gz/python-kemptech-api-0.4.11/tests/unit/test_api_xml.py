from nose.tools import assert_equal, assert_is_none

# handle py3 and py2 cases:
try:
    import unittest.mock as mock
except ImportError:
    import mock

patch = mock.patch

import python_kemptech_api.api_xml as api_xml


def test_is_successful_str():
    with patch.object(api_xml,'get_success_msg') as get_success_msg:
        get_success_msg.return_value = 'any string'
        res = api_xml.is_successful('any_xml')
        assert_equal(res, True)


def test_is_successful_None():
    with patch.object(api_xml,'get_success_msg') as get_success_msg:
        get_success_msg.return_value =None
        res = api_xml.is_successful('any_xml')
        assert_equal(res, False)


def test_get_xml_field_no_data_field():
    with patch.object(api_xml,'xmltodict') as xmltodict:
        xmltodict.parse.return_value = {'Response':{'myfield': 'myfield-value'}}
        res = api_xml._get_xml_field('any_xml', 'myfield')
        assert_equal(res, 'myfield-value')


def test_get_xml_field_with_data_field():
    with patch.object(api_xml,'xmltodict') as xmltodict:
        xmltodict.parse.return_value = {
        'Response':{'Success': {'myfield': {
             'mydata': 'mydata-value'}}}}
        res = api_xml._get_xml_field('any_xml', 'myfield', 'mydata')
        assert_equal(res, 'mydata-value')

def test_get_xml_field_with_KeyError():
    with patch.object(api_xml,'xmltodict') as xmltodict:
        xmltodict.parse.return_value = {}
        res = api_xml._get_xml_field('any_xml', 'myfield')
        assert_is_none(res)
