from nose.tools import (assert_equal, assert_is_instance,
                        assert_raises, assert_false,
                        assert_in)
try:
    from unittest.mock import (mock_open, patch,
                               MagicMock, sentinel)
except ImportError:
    from mock import (mock_open, patch,
                      MagicMock, sentinel)
from requests import exceptions

import python_kemptech_api.client as client


class MyError(Exception):
    pass



class Test_HttpClient_as_context_manager:

    def test_context_manager_enter(self):
        with client.HttpClient() as aclient:
            assert_is_instance(aclient, client.HttpClient)

    def test_context_manager_exit(self):
        with assert_raises(MyError):
            with client.HttpClient():
                raise MyError('An Error')


class Test_HttpClient_do_request:

    def setup(self):
        self.p_requests = patch.object(client, 'requests')
        requests = self.p_requests.start()

        self.response = MagicMock()
        self.response.status_code = 200
        self.response.text = sentinel.response_text
        self.request = requests.request
        self.request.return_value = self.response

        self.client = client.HttpClient()
        self.client.endpoint = 'ep/'

    def teardown(self):
        self.p_requests.stop()

    def test_no_file_parameter_set(self):
        open_ = mock_open(read_data='myData')
        with patch.object(client, "open", open_, create=True): # as my_open:
           self.client._do_request('GET','MyCommand')
           args = self.request.call_args
           # check positional arguments
           assert_equal(args[0], ('GET', 'ep/MyCommand?'))
           # check kwargs
           kw = args[1]
           assert_equal(kw['verify'], False)
           assert_equal(kw['params'], None)
           assert_false('data' in kw)

    def test_file_parameter_set(self):
        open_ = mock_open(read_data='myData')
        with patch.object(client, "open", open_, create=True): # as my_open:
           self.client._do_request('GET','MyCommand',
                                                parameters=sentinel.params,
                                                file='my_filename')
           args = self.request.call_args
           # check positional arguments
           assert_equal(args[0], ('GET', 'ep/MyCommand?'))
           # check kwargs
           kw = args[1]
           assert_equal(kw['params'], sentinel.params)
           assert_in('data', kw)

    def test_400_status_code(self):
        self.response.status_code = 400
        res = self.client._do_request('GET','MyCommand')
        assert_equal(res, sentinel.response_text)

    def test_401_status_code(self):
        with assert_raises(client.KempTechApiException):
            self.response.status_code = 401
            self.client._do_request('GET','MyCommand')

    # we test all the exceptions to confirm no errors will arise is their
    # call

    def test_re_raised_exceptions(self):
        my_exceptions = (exceptions.ConnectionError,
                                     exceptions.URLRequired,
                                     exceptions.TooManyRedirects,
                                     exceptions.Timeout,
                                     exceptions.RequestException)
        for e in my_exceptions:
            self.response.raise_for_status.side_effect = e
            with assert_raises(e):
                self.client._do_request('GET','MyCommand')

    def test_ConnectionTimeoutException(self):
        self.response.raise_for_status.side_effect = \
                exceptions.ConnectTimeout
        with assert_raises(client.ConnectionTimeoutException):
            self.client._do_request('GET','MyCommand')

    def test_HttpError(self):
        # this raises a KempTechApiException, whose
        # constructor expects an xml message, so we have
        # to choose a careful path through
        #  KempTechApiException.__init__

        self.response.text = None
        self.response.status_code = 999

        self.response.raise_for_status.side_effect = \
                exceptions.HTTPError
        with assert_raises(client.KempTechApiException):
            self.client._do_request('GET','MyCommand')
