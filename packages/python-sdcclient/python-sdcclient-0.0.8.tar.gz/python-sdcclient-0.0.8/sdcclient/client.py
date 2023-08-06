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


import uuid
import re

from keystoneclient.v2_0 import Client as KeystoneClient

from sdcclient.utils.rest_client_utils import HEADER_REPRESENTATION_XML, HEADER_CONTENT_TYPE, HEADER_TRANSACTION_ID
from sdcclient.utils.logger_utils import get_logger
from sdcclient.productandrelease_resource_client import ProductAndReleaseResourceClient

logger = get_logger(__name__)

# HEADERS
X_AUTH_TOKEN = "X-Auth-Token"
TENANT_ID = "Tenant-Id"

# TRANSACTION ID
TRANSACTION_ID_PATTERN = "qa/{uuid}"

# SERVICE
SDC_SERVICE_TYPE = "sdc"
SDC_ENDPOINT_TYPE = "publicURL"


def generate_transaction_id():
    """
    Generate a transaction ID value following defined pattern.
    :return: New transactionId
    """

    return TRANSACTION_ID_PATTERN.format(uuid=uuid.uuid4())


class SDCClient():

    headers = dict()
    keystone_client = None

    def __init__(self, username, password, tenant_id, auth_url, region_name, service_type=SDC_SERVICE_TYPE,
                 endpoint_type=SDC_ENDPOINT_TYPE):
        """
        Init Nova-Client. Url will be loaded from Keystone Service Catalog (publicURL, compute service)
        :param username: Fiware username
        :param password: Fiware password
        :param tenant_id: Fiware Tenant ID
        :param auth_url: Keystore URL
        :param region_name: Fiware Region name
        :param service_type: SDC Service type in Keystone (paasmanager by default)
        :param endpoint_type: SDC Endpoint type in Keystone (publicURL by default)
        :return: None
        """

        logger.info("Init SDC Client")
        logger.debug("Client parameters: Username: %s, Password: %s, TenantId: %s, AuthURL: %s, RegionName: %s, "
                     "ServiceType: %s, EndpointType: %s", username, password, tenant_id, auth_url, region_name,
                     service_type, endpoint_type)
        self.tenant_id = tenant_id

        self.__init_keystone_client__(username, password, tenant_id, auth_url)
        self.token = self.get_auth_token()
        self.init_headers(self.token, self.tenant_id)

        self.endpoint_url = self.get_sdc_endpoint_from_keystone(region_name, service_type, endpoint_type)

    def __init_keystone_client__(self, username, password, tenant_id, auth_url):
        """
        Init the keystone client to request token and endpoint data
        :param string username: Username for authentication.
        :param string password: Password for authentication.
        :param string tenant_id: Tenant id.
        :param string auth_url: Keystone service endpoint for authorization.
        :param string region_name: Name of a region to select when choosing an
                                   endpoint from the service catalog.
        :return None
        """

        logger.debug("Init Keystone Client")
        self.keystone_client = KeystoneClient(username=username, password=password, tenant_id=tenant_id,
                                              auth_url=auth_url)

    def get_auth_token(self):
        """
        Get token from Keystone
        :return: Token (String)
        """

        logger.debug("Getting auth Token")
        return self.keystone_client.auth_ref['token']['id']

    def get_sdc_endpoint_from_keystone(self, region_name, service_type, endpoint_type):
        """
        Get the endpoint of SDC from Keystone Service Catalog
        :param region_name: Name of the region
        :param service_type: Type of service (Endpoint name)
        :param endpoint_type: Type of the URL to look for
        :return:
        """

        logger.debug("Getting SDC endpoint")
        endpoint = None
        for service in self.keystone_client.auth_ref['serviceCatalog']:
            if service['name'] == service_type:
                for endpoint in service['endpoints']:
                    if endpoint['region'] == region_name:
                        endpoint = endpoint[endpoint_type]
                        break
                break
        logger.debug("SDC endpoint (Service: %s, Type: %s, Region: %s) is: %s", service_type, endpoint_type,
                     region_name, endpoint_type)
        return endpoint

    def init_headers(self, x_auth_token, tenant_id, content_type=HEADER_REPRESENTATION_XML,
                     transaction_id=generate_transaction_id()):
        """
        Init header to values (or default values)
        :param x_auth_token: Token from Keystone for tenant_id (OpenStack)
        :param tenant_id: TenantId (OpenStack)
        :param content_type: Content-Type header value. By default application/xml
        :param transaction_id: txId header value. By default, generated value by generate_transaction_id()
        :return: None
        """

        logger.debug("Init headers")
        if content_type is None:
            if HEADER_CONTENT_TYPE in self.headers:
                del(self.headers[HEADER_CONTENT_TYPE])
        else:
            self.headers.update({HEADER_CONTENT_TYPE: content_type})

        if transaction_id is None:
            if HEADER_TRANSACTION_ID in self.headers:
                del(self.headers[HEADER_TRANSACTION_ID])
        else:
            self.headers.update({HEADER_TRANSACTION_ID: transaction_id})

        self.headers.update({X_AUTH_TOKEN: x_auth_token})

        self.headers.update({TENANT_ID: tenant_id})

        logger.debug("Headers: " + str(self.headers))

    def set_headers(self, headers):
        """
        Set header.
        :param headers: Headers to be used by next request (dict)
        :return: None
        """

        logger.debug("Setting headers: " + str(headers))
        self.headers = headers

    def getProductAndReleaseResourceClient(self):
        """
        Create an API resource REST client
        :return: Rest client for 'Environment' API resource
        """
        split_regex = "(.*)://(.*):(\d*)/(.*)"
        regex_matches = re.search(split_regex, self.endpoint_url)

        logger.info("Creating ProductAndReleaseResourceClient")

        return ProductAndReleaseResourceClient(protocol=regex_matches.group(1), host=regex_matches.group(2),
                                        port=regex_matches.group(3), tenant_id=self.tenant_id,
                                        resource=regex_matches.group(4), headers=self.headers)


