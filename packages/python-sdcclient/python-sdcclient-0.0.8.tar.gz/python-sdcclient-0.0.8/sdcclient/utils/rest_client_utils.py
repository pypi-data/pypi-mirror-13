# -*- coding: utf-8 -*-

# Copyright 2015 Telefonica Investigación y Desarrollo, S.A.U
#
# This file is part of FIWARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es


import requests
import xmltodict
import xmldict
from json import JSONEncoder
from logger_utils import get_logger, log_print_request, log_print_response

requests.packages.urllib3.disable_warnings()
logger = get_logger(__name__)


# HEADERS
HEADER_CONTENT_TYPE = u'content-type'
HEADER_ACCEPT = u'accept'
HEADER_REPRESENTATION_JSON = u'application/json'
HEADER_REPRESENTATION_XML = u'application/xml'
HEADER_REPRESENTATION_TEXTPLAIN = u'text/plain'
HEADER_AUTH_TOKEN = u'X-Auth-Token'
HEADER_TENANT_ID = u'Tenant-Id'
HEADER_TRANSACTION_ID = u'txid'

# HTTP VERBS
HTTP_VERB_POST = 'post'
HTTP_VERB_GET = 'get'
HTTP_VERB_PUT = 'put'
HTTP_VERB_DELETE = 'delete'
HTTP_VERB_UPDATE = 'update'


# REST CLIENT PATTERS
API_ROOT_URL_ARG_NAME = 'api_root_url'
URL_ROOT_PATTERN = "{protocol}://{host}:{port}"


class RestClient(object):

    api_root_url = None

    def __init__(self, protocol, host, port, resource=None):
        """
        Init the RestClient with an URL ROOT Pattern using the specified params
        :param protocol: Web protocol [HTTP | HTTPS] (string)
        :param host: Hostname or IP (string)
        :param port: Service port (string)
        :param resource: Base URI resource, if exists (string)
        :return: None
        """

        self.api_root_url = self._generate_url_root(protocol, host, port)
        if resource is not None:
            self.api_root_url += "/" + resource

    @staticmethod
    def _generate_url_root(protocol, host, port):
        """
        Generate API root URL without resources
        :param protocol: Web protocol [HTTP | HTTPS] (string)
        :param host: Hostname or IP (string)
        :param port: Service port (string)
        :return: ROOT url
        """
        return URL_ROOT_PATTERN.format(protocol=protocol, host=host, port=port)

    def _call_api(self, uri_pattern, method, body=None, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax)
        :param method: HTTP method to execute (string) [get | post | put | delete | update]
        :param body: Raw Body content (string) (Plain/XML/JSON to be sent)
        :param headers: HTTP header request (dict)
        :param parameters: Query parameters for the URL. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without API_ROOT_URL_ARG_NAME) to fill the patters
        :returns: REST API response ('Requests' response)
        """

        kwargs[API_ROOT_URL_ARG_NAME] = self.api_root_url
        url = uri_pattern.format(**kwargs)
        logger.info("Executing API request [%s %s]", method, url)

        log_print_request(logger, method, url, parameters, headers, body)

        try:
            response = requests.request(method=method, url=url, data=body, headers=headers, params=parameters,
                                        verify=False)
        except Exception, e:
            logger.error("Request {} to {} crashed: {}".format(method, url, str(e)))
            raise e

        log_print_response(logger, response)

        return response

    def launch_request(self, uri_pattern, body, method, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax)
        :param body: Raw Body content (string) (Plain/XML/JSON to be sent)
        :param method: HTTP ver to be used in the request [GET | POST | PUT | DELETE | UPDATE ]
        :param headers: HTTP header (dict)
        :param parameters: Query parameters for the URL. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :returns: REST API response ('Requests' response)
        """
        return self._call_api(uri_pattern, method, body, headers, parameters, **kwargs)

    def get(self, uri_pattern, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP GET request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax)
        :param headers: HTTP header (dict)
        :param parameters: Query parameters. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :returns: REST API response ('Requests' response)
        """
        print uri_pattern
        print headers
        return self._call_api(uri_pattern, HTTP_VERB_GET, headers=headers, parameters=parameters, **kwargs)

    def post(self, uri_pattern, body, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP POST request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax)
        :param body: Raw Body content (string) (Plain/XML/JSON to be sent)
        :param headers: HTTP header (dict)
        :param parameters: Query parameters. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :returns: REST API response ('Requests' response)
        """
        return self._call_api(uri_pattern, HTTP_VERB_POST, body, headers, parameters, **kwargs)

    def put(self, uri_pattern, body, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP PUT request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax)
        :param body: Raw Body content (string) (Plain/XML/JSON to be sent)
        :param headers: HTTP header (dict)
        :param parameters: Query parameters. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :returns: REST API response ('Requests' response)
        """
        return self._call_api(uri_pattern, HTTP_VERB_PUT, body, headers, parameters, **kwargs)

    def delete(self, uri_pattern, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP DELETE request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax)
        :param headers: HTTP header (dict)
        :param parameters: Query parameters. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :returns: REST API response ('Requests' response)
        """
        return self._call_api(uri_pattern, HTTP_VERB_DELETE, headers=headers, parameters=parameters, **kwargs)


def _xml_to_dict(xml_to_convert):
    """
    Convert RAW XML string to Python dict
    :param xml_to_convert: XML to convert (string/text)
    :return: Python dict with all XML data
    """

    logger.debug("Converting to Python dict this XML: " + str(xml_to_convert))
    return xmltodict.parse(xml_to_convert, attr_prefix='')


def _dict_to_xml(dict_to_convert):
    """
    Convert Python dict to XML
    :param dict_to_convert: Python dict to be converted (dict)
    :return: XML (string)
    """

    logger.debug("Converting to XML the Python dict: " + str(dict_to_convert))
    return xmldict.dict_to_xml(dict_to_convert)


def response_body_to_dict(http_requests_response, content_type, xml_root_element_name=None, is_list=False):
    """
    Convert a XML or JSON response in a Python dict
    :param http_requests_response: 'Requests (lib)' response
    :param content_type: Expected content-type header value (Accept header value in the request)
    :param xml_root_element_name: For XML requests. XML root element in response.
    :param is_list: For XML requests. If response is a list, a True value will delete list node name
    :return: Python dict with response.
    """

    logger.info("Converting response body from API (XML or JSON) to Python dict")
    if HEADER_REPRESENTATION_JSON == content_type:
        try:
            return http_requests_response.json()
        except Exception, e:
            logger.error("Error parsing the response to JSON. Exception:" + str(e))
            raise e
    else:
        assert xml_root_element_name is not None,\
            "xml_root_element_name is a mandatory param when body is in XML"

        try:
            response_body = _xml_to_dict(http_requests_response.content)[xml_root_element_name]
        except Exception, e:
            logger.error("Error parsing the response to XML. Exception: " + str(e))
            raise e

        if is_list and response_body is not None:
            response_body = response_body.popitem()[1]

        return response_body


def model_to_request_body(body_model, content_type, body_model_root_element=None):
    """
    Convert a Python dict (body model) to XML or JSON
    :param body_model: Model to be parsed. This model should have a root element.
    :param content_type: Target representation (Content-Type header value)
    :param body_model_root_element: For XML requests. XML root element in the model (if exists).
    :return:
    """

    logger.info("Converting body request model (Python dict) to JSON or XML")
    if HEADER_REPRESENTATION_XML == content_type:
        try:
            return _dict_to_xml(body_model)
        except Exception, e:
            logger.error("Error parsing the body model to XML. Exception: " + str(e))
            raise e
    else:
        body_json = body_model[body_model_root_element] if body_model_root_element is not None else body_model
        encoder = JSONEncoder()

        try:
            return encoder.encode(body_json)
        except Exception, e:
            logger.error("Error parsing the body model to JSON. Exception:" + str(e))
            raise e

def delete_element_when_value_none(data_structure):
    """
    This method remove all entries in a Python dict when its value is None.
    :param data_structure: Python dict (lists are supported). e.i:
            [{"element1": "e1",
              "element2": {"element2.1": "e2",
                        "element2.2": None},
              "element3": "e3"},
            {"elementA": "eA",
             "elementB": {"elementB.1": None,
             "elementB2": ["a", "b"]}}]
    :return: None. The data_structure is modified
    """
    if isinstance(data_structure, list):
        for element in data_structure:
            delete_element_when_value_none(element)
    elif isinstance(data_structure, dict):
        for element in data_structure.keys():
            if data_structure[element] is None:
                del data_structure[element]
            else:
                delete_element_when_value_none(data_structure[element])
                if len(data_structure[element]) == 0:
                        del data_structure[element]
