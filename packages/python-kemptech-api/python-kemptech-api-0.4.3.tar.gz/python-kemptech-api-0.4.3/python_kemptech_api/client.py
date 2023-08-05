import os
import subprocess
import logging

import requests
from requests import exceptions

from python_kemptech_api.api_xml import (
    get_error_msg, is_successful,
    get_data_field, parse_to_dict,
    get_data)
from python_kemptech_api.exceptions import (
    KempTechApiException,
    CommandNotAvailableException,
    ConnectionTimeoutException,
    VirtualServiceMissingLoadmasterInfo,
    RealServerMissingLoadmasterInfo,
    RealServerMissingVirtualServiceInfo,
    LoadMasterParameterError
)

requests.packages.urllib3.disable_warnings()
log = logging.getLogger(__name__)


class HttpClient(object):
    """Client that performs HTTP requests."""

    ip_address = None
    endpoint = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def _do_request(self, http_method, rest_command,
                    parameters=None,
                    file=None):
        """Perform a HTTP request.

        :param http_method: GET or POST.
        :param rest_command: The command to run.
        :param parameters: dict containing parameters.
        :param file: Location of file to send.
        :return: The Status code of request and the response text body.
        """
        response = None
        cmd_url = "{endpoint}{cmd}?".format(endpoint=self.endpoint,
                                            cmd=rest_command)
        log.debug("Request is: %s", cmd_url)

        try:
            if file is not None:
                with open(file, 'rb') as payload:
                    response = requests.request(http_method, cmd_url,
                                                params=parameters,
                                                verify=False,
                                                data=payload)
            else:
                response = requests.request(http_method, cmd_url,
                                            params=parameters,
                                            timeout=5,
                                            verify=False)
            if 400 < response.status_code < 500:
                raise KempTechApiException(code=response.status_code)
            else:
                response.raise_for_status()
        except exceptions.ConnectTimeout:
            log.error("The connection timed out to %s.", self.ip_address)
            raise ConnectionTimeoutException(self.ip_address)
        except exceptions.ConnectionError:
            log.error("A connection error occurred to %s.", self.ip_address)
            raise
        except exceptions.URLRequired:
            log.error("%s is an invalid URL", cmd_url)
            raise
        except exceptions.TooManyRedirects:
            log.error("Too many redirects with request to %s.", cmd_url)
            raise
        except exceptions.Timeout:
            log.error("A connection %s has timed out.", self.ip_address)
            raise
        except exceptions.HTTPError:
            log.error("A HTTP error occurred with request to %s.", cmd_url)
            raise KempTechApiException(msg=response.text,
                                       code=response.status_code)
        except exceptions.RequestException:
            log.error("An error occurred with request to %s.", cmd_url)
            raise
        return response.text

    def _get(self, rest_command, parameters=None):
        return self._do_request('GET', rest_command, parameters)

    def _post(self, rest_command, file=None, parameters=None):
        return self._do_request('POST', rest_command, parameters=parameters,
                                file=file)

# ---- Models ---


def send_response(response):
    """send the given response if ok.

    :param response: the response to send
    :type response: Response
    :raises: KempTechApiErrorError
    """
    if is_successful(response):
        return parse_to_dict(response)
    else:
        raise KempTechApiException(get_error_msg(response))


class LoadMaster(HttpClient):
    """LoadMaster API object."""

    def __init__(self, ip, username, password, port=443):
        self.ip_address = ip
        self.username = username
        self.password = password
        self.port = port

    def __repr__(self):
        return '{}:{}'.format(self.ip_address, self.port)

    @property
    def endpoint(self):
        return "https://{user}:{pw}@{ip}:{port}/access".format(
            user=self.username,
            pw=self.password,
            ip=self.ip_address,
            port=self.port
        )

    @property
    def get_loadmaster_info(self):
        return {
            "endpoint": self.endpoint,
            "ip_address": self.ip_address,
        }

    def create_virtual_service(self, ip, port=80, protocol="tcp"):
        """VirtualService factory with pre-configured LoadMaster connection."""
        vs = VirtualService(self.get_loadmaster_info, ip, port, protocol)
        return vs

    def get_virtual_services(self):
        response = self._get("/listvs")
        data = get_data(response)
        virtual_services = []
        for service in data.get('VS', []):
            virt_serv = self.build_virtual_service(service)
            virtual_services.append(virt_serv)
        return virtual_services

    def get_virtual_service(self, index=None, address=None, port=None,
                            protocol=None):
        if index is None:
            service_id = {"vs": address, "port": port, "prot": protocol}
        else:
            service_id = {"vs": index}
        response = self._get("/showvs", service_id)
        service = get_data(response)
        virt_serv = self.build_virtual_service(service)
        return virt_serv

    def build_virtual_service(self, service):
        """Create a VirtualService instance with standard defaults"""
        virt_serv = VirtualService(self.get_loadmaster_info,
                                   service.get('VSAddress', None),
                                   service.get('VSPort'),
                                   service.get('Protocol'))
        virt_serv.status = service.get('Status', None)
        virt_serv.index = service.get('Index', None)
        virt_serv.enable = service.get('Enable', None)
        virt_serv.forcel7 = service.get('ForceL7', None)
        virt_serv.vstype = service.get('VStype', None)
        virt_serv.schedule = service.get('Schedule', None)
        virt_serv.nickname = service.get('NickName', None)
        return virt_serv

    def set_parameter(self, parameter, value):
        """assign the value to the given loadmaster parameter

        :param parameter: a valid LoadMaster parameter.
        :type parameter: str.
        :param value: the value to be assigned
        :type value: str.
        :raises: LoadMasterParameterError
        """
        parameters = {
            'param': parameter,
            'value': value,
        }
        response = self._get('/set', parameters)
        if not is_successful(response):
            raise LoadMasterParameterError(self, parameters)

    def get_parameter(self, parameter):
        """get the value of the given LoadMaster parameter

        :param parameter: a valid LoadMaster parameter.
        :type parameter: str.
        :return: str -- the parameter value
        """
        parameters = {
            'param': parameter,
        }
        response = self._get('/get', parameters)
        value = get_data_field(response, parameter)
        if isinstance(value, dict):
            # This hack converts possible HTML to an awful one string
            # disaster instead of returning parsed html as an OrderedDict.
            value = "".join("{!s}={!r}".format(key, val) for (key, val) in
                            sorted(value.items()))
        return value

    def enable_api(self):
        """enable LoadMaster API"""
        # Can't use the HttpClient methods for this as the
        # endpoint is different when attempting to enable the API.
        url = ("https://{user}:{pw}@{ip}:{port}"
               "/progs/doconfig/enableapi/set/yes").format(user=self.username,
                                                           pw=self.password,
                                                           ip=self.ip_address,
                                                           port=self.port)
        try:
            requests.get(url, verify=False, timeout=1)
            return True
        except exceptions.RequestException:
            return False

    def stats(self):
        response = self._get('/stats')
        return send_response(response)

    def update_firmware(self, file):
        response = self._post('/installpatch', file)
        return is_successful(response)

    def shutdown(self):
        response = self._get('/shutdown')
        return is_successful(response)

    def reboot(self):
        response = self._get('/reboot')
        return is_successful(response)

    def get_sdn_controller(self):
        response = self._get('/getsdncontroller')
        return send_response(response)

    def get_license_info(self):
        try:
            response = self._get('360/licenseinfo')
            return send_response(response)

        except KempTechApiException:
            raise CommandNotAvailableException(
                self, '/access360/licenseinfo')

    def list_addons(self):
        response = self._get('/listaddon')
        return send_response(response)

    def upload_template(self, file):
        response = self._post('/uploadtemplate', file)
        return send_response(response)

    def list_templates(self):
        response = self._get('/listtemplates')
        return send_response(response)

    def delete_template(self, template_name):
        params = {'name': template_name}
        response = self._get('/deltemplate', parameters=params)
        return send_response(response)

    def apply_template(self, virtual_ip, port, protocol, template_name):
        params = {
            'vs': virtual_ip,
            'port': port,
            'prot': protocol,
            'name': template_name,
        }
        response = self._get('/addvs', parameters=params)
        return send_response(response)

    def get_sdn_info(self):
        response = self._get('/sdninfo')
        return send_response(response)

    def restore_backup(self, backup_type, file):
        # 1 LoadMaster Base Configuration
        # 2 Virtual Service Configuration
        # 3 GEO Configuration
        if backup_type not in [1, 2, 3]:
            backup_type = 2
        params = {"type": backup_type}
        response = self._post('/restore', file=file,
                              parameters=params)
        return send_response(response)

    def backup(self):
        # Dirty API, dirty hack.

        if not os.path.exists('backups'):
            os.makedirs('backups')
        file_name = "backups/{}.backup".format(self.ip_address)

        with open(file_name, 'wb') as file:
            curl = ['curl', '-k', '{}/backup'.format(self.endpoint)]
            subprocess.call(curl, stdout=file)
        return file_name

    def alsi_license(self, kemp_id, password):
        params = {
            "kemp_id": kemp_id,
            "password": password,
        }
        response = self._get('/alsilicense', parameters=params)
        return send_response(response)

    def set_initial_password(self, password):
        params = {"passwd": password}
        response = self._get('/set_initial_password', parameters=params)
        return send_response(response)

    def kill_asl_instance(self):
        response = self._get('/killaslinstance')
        return send_response(response)


class KempBaseObjectModel(object):
    # blacklist attributes that shouldn't be pushed to the loadmaster.
    _API_IGNORE = (
        "ip_address",
        "endpoint",
    )

    def __repr__(self):
        return '{} {}'.format(self.__class__.__name__, self.to_api_dict())

    def to_api_dict(self):
        """returns API related attributes as a dict

        Ignores attributes listed in _api_ignore and also attributes
        beginning with an underscore (_). Also ignore values of None"""
        api_dict = {}
        for key, value in self.__dict__.items():
            if (key in self._API_IGNORE or key.startswith("_") or
                    value is None):
                continue
            api_dict[key] = value
        return api_dict


class VirtualService(HttpClient, KempBaseObjectModel):

    def __init__(self, loadmaster_info, ip, port=80, prot="tcp"):
        self.vs = ip
        self.port = port
        self.prot = prot
        try:
            self.endpoint = loadmaster_info["endpoint"]
        except KeyError:
            raise VirtualServiceMissingLoadmasterInfo("endpoint")
        try:
            self.ip_address = loadmaster_info["ip_address"]
        except KeyError:
            raise VirtualServiceMissingLoadmasterInfo("ip_address")
        super(VirtualService, self).__init__()

    def __str__(self):
        return 'Virtual Service {} {}:{} on LoadMaster {}'.format(
            self.prot.upper(), self.vs, self.port, self.ip_address)

    def _get_base_parameters(self):
        """Returns the bare minimum VS parameters. IP, port and protocol"""
        return {"vs": self.vs, "port": self.port, "prot": self.prot}

    @property
    def get_virtual_service_info(self):
        return {
            "endpoint": self.endpoint,
            "ip_address": self.ip_address,
            "vs": self.vs,
            "port": self.port,
            "prot": self.prot,
        }

    def save(self, update=False):
        if not update:
            response = self._get("/addvs", self._get_base_parameters())
        else:
            response = self._get("/modvs", self.to_api_dict())
        if is_successful(response):
            vs_data = get_data(response)
            self.populate_virtual_service_attributes(vs_data)
        else:
            raise KempTechApiException(get_error_msg(response))

    def delete(self):
        response = self._get("/delvs", self._get_base_parameters())
        return send_response(response)

    def populate_virtual_service_attributes(self, service):
        """Populate VirtualService instance with standard defaults"""
        self.status = service.get('Status', None)
        self.index = service.get('Index', None)
        self.enable = service.get('Enable', None)
        self.forcel7 = service.get('ForceL7', None)
        self.vstype = service.get('VStype', None)
        self.schedule = service.get('Schedule', None)
        self.nickname = service.get('NickName', None)

    def create_real_server(self, ip, port=80):
        """RealServer factory with pre-configured LoadMaster connection."""
        loadmaster_virt_service_info = self._get_base_parameters()
        loadmaster_virt_service_info.vs = self.vs
        loadmaster_virt_service_info.port = self.port
        loadmaster_virt_service_info.prot = self.prot
        rs = RealServer(loadmaster_virt_service_info, ip, port)
        return rs

    def get_real_server(self, index=None, address=None, port=None,
                        protocol=None, real_server_address=None,
                        real_server_port=None):
        if index is None:
            server_id = {
                "vs": address,
                "port": port,
                "prot": protocol,
                "rs": real_server_address,
                "rsport": real_server_port,
            }
            response = self._get("/showrs", server_id)
        else:
            server_id = {
                "vs": index,
                "rs": real_server_address,
                "rsport": real_server_port,
            }
            response = self._get("/showrs", server_id)
        response_data = get_data(response)
        server = response_data["Rs"]
        real_server = self.build_real_server(server)
        return real_server

    def get_real_servers(self):
        response = self._get("/showvs", self._get_base_parameters())
        data = get_data(response)
        real_servers = []
        for server in data.get('Rs', []):
            real_server = self.build_real_server(server)
            real_servers.append(real_server)
        return real_servers

    def build_real_server(self, server):
        real_server = RealServer(self.get_virtual_service_info,
                                 server.get('Addr', None),
                                 server.get('Port', None))
        real_server.status = server.get('Status', None)
        real_server.forward = server.get('Forward', None)
        real_server.enable = server.get('Enable', None)
        real_server.weight = server.get('Weight', None)
        real_server.limit = server.get('Limit', None)
        return real_server


class RealServer(HttpClient, KempBaseObjectModel):

    def __init__(self, loadmaster_virt_service_info, ip, port=80):
        self.rs = ip
        self.rsport = port
        try:
            self.vs = loadmaster_virt_service_info["vs"]
        except KeyError:
            raise RealServerMissingVirtualServiceInfo("vs")

        self.port = loadmaster_virt_service_info.get("port", None)
        self.prot = loadmaster_virt_service_info.get("prot", None)
        try:
            self.endpoint = loadmaster_virt_service_info["endpoint"]
        except KeyError:
            raise RealServerMissingLoadmasterInfo("endpoint")

        try:
            self.ip_address = loadmaster_virt_service_info["ip_address"]
        except KeyError:
            raise RealServerMissingLoadmasterInfo("ip_address")

        super(RealServer, self).__init__()

    def __str__(self):
        return 'Real Server {} on Virtual Service {} {}:{}'.format(
            self.rs, self.prot.upper(), self.vs, self.port)

    def _get_base_parameters(self):
        """Returns the bare minimum VS parameters. IP, port and protocol"""
        return {
            "vs": self.vs,
            "port": self.port,
            "prot": self.prot,
            "rs": self.rs,
            "rsport": self.rsport,
        }

    def save(self, update=False):
        if not update:
            response = self._get("/addrs", self._get_base_parameters())
        else:
            response = self._get("/modrs", self.to_api_dict())
        return send_response(response)

    def delete(self):
        response = self._get("/delrs", self._get_base_parameters())
        return send_response(response)
