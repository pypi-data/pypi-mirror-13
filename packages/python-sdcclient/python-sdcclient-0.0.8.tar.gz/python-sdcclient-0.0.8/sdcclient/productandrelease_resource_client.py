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


from sdcclient.utils.rest_client_utils import RestClient, API_ROOT_URL_ARG_NAME, response_body_to_dict, \
    HEADER_CONTENT_TYPE, HEADER_REPRESENTATION_XML
from sdcclient.utils.logger_utils import get_logger

logger = get_logger(__name__)


#URI ELEMENT
SDC_BASE_URI = "{" + API_ROOT_URL_ARG_NAME + "}"
PRODUCTANDRELEASE_RESOURCE_ROOT_URI = SDC_BASE_URI + "/catalog/productandrelease"
PRODUCTANDRELEASE_RESOURCE_DETAIL_URI = PRODUCTANDRELEASE_RESOURCE_ROOT_URI + "/{environment_name}"

#BODY ELEMENT
PRODUCTANDRELEASE_BODY_ROOT= "productAndReleaseDtoes"

class ProductAndReleaseResourceClient(RestClient):

    def __init__(self, protocol, host, port, tenant_id, resource=None, headers=None):
        """
        Class constructor. Inits default attributes.
        :param protocol: Connection protocol (HTTP | HTTPS)
        :param host: Host
        :param port: Port
        :param tenant_id: TenantID
        :param resource: Base URI resource
        :param headers: HTTP Headers
        :return: None
        """
        if headers is None:
            self.headers = {HEADER_CONTENT_TYPE: HEADER_REPRESENTATION_XML}
        self.headers = headers
        self.tenant_id = tenant_id
        super(ProductAndReleaseResourceClient, self).__init__(protocol, host, port, resource=resource)

    def get_allproductandrelease(self):
        """
        Get All ProductAndReleases
        :return: A duple: All product and Releses from SDC Catalog as a dict, the 'Request' response
        """
        logger.info("Get all ProductAndReleases")
        response = self.get(PRODUCTANDRELEASE_RESOURCE_ROOT_URI, headers=self.headers)
        sr_response = response_body_to_dict(response, self.headers[HEADER_CONTENT_TYPE],
                                          xml_root_element_name=PRODUCTANDRELEASE_BODY_ROOT)
        return sr_response, response
