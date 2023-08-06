# Copyright 2011 OpenStack Foundation
# Copyright 2013 Rackspace Hosting
# Copyright 2013 Hewlett-Packard Development Company, L.P.
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

"""
OpenStack Client interface. Handles the REST calls and responses.
"""

from __future__ import print_function

import os
import logging
import requests
import pkg_resources
import json

from cdbclient.openstack.common.apiclient import client
from cdbclient.openstack.common.apiclient import exceptions
from cdbclient.openstack.common import importutils
from cdbclient import service_catalog
from cdbclient.extension import Extension

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

try:
    import eventlet as sleep_lib
except ImportError:
    import time as sleep_lib


class HTTPClient(object):

    USER_AGENT = 'python-troveclient'

    def __init__(self, user, password, projectid, auth_url=None,
                 insecure=False, timeout=None, tenant_id=None,
                 region_name=None, endpoint_type='publicURL',
                 service_type=None, service_name=None, retries=None,
                 http_log_debug=False, cacert=None, bypass_url=None,
                 auth_system='keystone', auth_plugin=None,
                 http_log_to_stream=False):

        self.user = user
        self.password = password
        self.projectid = projectid
        self.tenant_id = tenant_id
        self.auth_url = auth_url.rstrip('/') if auth_url else auth_url
        self.version = 'v1'
        self.region_name = region_name
        self.endpoint_type = endpoint_type
        self.service_type = service_type
        self.service_name = service_name
        self.retries = int(retries or 0)
        self.http_log_debug = http_log_debug
        self.management_url = None
        self.auth_token = None
        self.timeout = timeout
        self.bypass_url = bypass_url
        self.auth_system = auth_system

        if insecure:
            self.verify_cert = False
        else:
            if cacert:
                self.verify_cert = cacert
            else:
                self.verify_cert = True

        self._logger = logging.getLogger(__name__)
        if http_log_to_stream and not self._logger.handlers:
            ch = logging.StreamHandler()
            self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(ch)
            if hasattr(requests, 'logging'):
                requests.logging.getLogger(requests.__name__).addHandler(ch)

    def http_log_req(self, args, kwargs):
        string_parts = ['curl -i']
        for element in args:
            if element in ('GET', 'POST', 'DELETE', 'PUT'):
                string_parts.append(' -X %s' % element)
            else:
                string_parts.append(' %s' % element)

        for element in kwargs['headers']:
            header = ' -H "%s: %s"' % (element, kwargs['headers'][element])
            string_parts.append(header)

        if 'data' in kwargs:
            string_parts.append(" -d '%s'" % (kwargs['data']))
        self._logger.debug("\nREQ: %s\n" % "".join(string_parts))

    def http_log_resp(self, resp):
        if not self.http_log_debug:
            return
        try:
            text = json.dumps(resp.json(), indent=4)
        except:
            text = resp.text
        self._logger.debug(
            "RESP: [%s] %s\nRESP BODY: %s\n",
            resp.status_code,
            resp.headers,
            text)

    def request(self, url, method, **kwargs):
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        kwargs['headers']['User-Agent'] = self.USER_AGENT
        kwargs['headers']['Accept'] = 'application/json'
        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs['body'])
            del kwargs['body']

        if self.timeout:
            kwargs.setdefault('timeout', self.timeout)
        self.http_log_req((url, method,), kwargs)
        resp = requests.request(
            method,
            url,
            verify=self.verify_cert,
            **kwargs)
        self.http_log_resp(resp)

        if resp.text:
            try:
                body = json.loads(resp.text)
            except ValueError:
                pass
                body = None
        else:
            body = None

        # Save the last reponse and status code
        self.last_response = resp, body
        self.last_http_code = resp.status_code

        if resp.status_code >= 400:
            raise exceptions.from_response(resp, body, url)
        return resp, body

    def _cs_request(self, url, method, **kwargs):
        auth_attempts = 0
        attempts = 0
        backoff = 1
        while True:
            attempts += 1
            if not self.management_url or not self.auth_token:
                self.authenticate()
            kwargs.setdefault('headers', {})['X-Auth-Token'] = self.auth_token
            if self.projectid:
                kwargs['headers']['X-Auth-Project-Id'] = self.projectid
            try:
                resp, body = self.request(self.management_url + url, method,
                                          **kwargs)
                return resp, body
            except exceptions.BadRequest as e:
                if attempts > self.retries:
                    raise
            except exceptions.Unauthorized:
                if auth_attempts > 0:
                    raise
                self._logger.debug("Unauthorized, reauthenticating.")
                self.management_url = self.auth_token = None
                # First reauth. Discount this attempt.
                attempts -= 1
                auth_attempts += 1
                continue
            except exceptions.ClientException as e:
                if attempts > self.retries:
                    raise
                if 500 <= e.code <= 599:
                    pass
                else:
                    raise
            except requests.exceptions.ConnectionError as e:
                # Catch a connection refused from requests.request
                self._logger.debug("Connection refused: %s" % e)
                msg = 'Unable to establish connection: %s' % e
                raise exceptions.ConnectionRefused(msg)
            self._logger.debug(
                "Failed attempt(%s of %s), retrying in %s seconds" %
                (attempts, self.retries, backoff))
            sleep_lib.sleep(backoff)
            backoff *= 2

    def get(self, url, **kwargs):
        return self._cs_request(url, 'GET', **kwargs)

    def patch(self, url, **kwargs):
        return self._cs_request(url, 'PATCH', **kwargs)

    def post(self, url, **kwargs):
        return self._cs_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self._cs_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self._cs_request(url, 'DELETE', **kwargs)

    def _extract_service_catalog(self, url, resp, body, extract_token=True):
        """See what the auth service told us and process the response.
        We may get redirected to another site, fail or actually get
        back a service catalog with a token and our endpoints.
        """

        if resp.status_code == 200:  # content must always present
            try:
                self.auth_url = url
                self.service_catalog = \
                    service_catalog.ServiceCatalog(body)

                if extract_token:
                    self.auth_token = self.service_catalog.get_token()

                if self.bypass_url:
                    management_url = self.bypass_url
                else:
                    management_url = self.service_catalog.url_for(
                        attr='region',
                        filter_value=self.region_name,
                        endpoint_type=self.endpoint_type,
                        service_type=self.service_type,
                        service_name=self.service_name)
                self.management_url = management_url.rstrip('/')
                return None
            except exceptions.AmbiguousEndpoints:
                print("Found more than one valid endpoint. Use a more "
                      "restrictive filter")
                raise
            except KeyError:
                raise exceptions.AuthorizationFailure()
            except exceptions.EndpointNotFound:
                print("Could not find any suitable endpoint. Correct region?")
                raise
        elif resp.status_code == 305:
            return resp['location']
        else:
            raise exceptions.from_response(resp, body, url)

    def authenticate(self):
        auth_url = self.auth_url
        while auth_url:
            if self.auth_system == 'keystone':
                auth_url = self._v2_auth(auth_url)
            elif self.auth_system in ['rax', 'rax2', 'rackspace']:
                auth_url = self._rax_auth(auth_url)
            elif self.auth_system == 'racker':
                auth_url = self._racker_auth(auth_url)
            elif self.auth_system == 'fake':
                auth_url = self._fake_auth(auth_url)

    def _v2_auth(self, url):
        """Authenticate against a v2.0 auth service."""
        body = {"auth": {
            "passwordCredentials": {"username": self.user,
                                    "password": self.password}}}

        if self.projectid:
            body['auth']['tenantName'] = self.projectid
        elif self.tenant_id:
            body['auth']['tenantId'] = self.tenant_id

        self._authenticate(url, body)

    def _rax_auth(self, url):
        body = {
            "auth": {
                "RAX-KSKEY:apiKeyCredentials": {
                    "username": self.user,
                    "apiKey": self.password
                }
            }
        }
        self._authenticate(url, body)

    def _racker_auth(self, url):
        body = {
            "auth": {
                "RAX-AUTH:domain": {
                    "name": "Rackspace"
                },
                "passwordCredentials": {
                    "username": self.user,
                    "password": self.password,
                }
            }
        }
        self._authenticate(url, body)

    def _fake_auth(self, url):
        body = {
            'access': {
                'token': {
                    'id': self.tenant_id
                },
                'serviceCatalog': []
            }
        }

        class FakeResponse:
            status_code = 200

        resp = FakeResponse()
        self._extract_service_catalog(url, resp, body)

    def _authenticate(self, url, body):
        """Authenticate and extract the service catalog."""
        if not url.endswith('tokens'):
            url = os.path.join(url, 'tokens')

        # Make sure we follow redirects when trying to reach Keystone
        resp, body = self.request(
            url,
            "POST",
            body=body,
            allow_redirects=True)

        return self._extract_service_catalog(url, resp, body)


def _construct_http_client(username=None, password=None, project_id=None,
                           auth_url=None, insecure=False, timeout=None,
                           region_name=None, endpoint_type='publicURL',
                           service_type='rax:database',
                           service_name='cloudDatabases',
                           retries=None,
                           http_log_debug=False,
                           auth_system='keystone', auth_plugin=None,
                           cacert=None, bypass_url=None, tenant_id=None,
                           session=None,
                           auth=None,
                           client_cls=None,
                           http_log_to_stream=None):

    client_cls = client_cls or HTTPClient
    return client_cls(username,
                      password,
                      projectid=project_id,
                      auth_url=auth_url,
                      insecure=insecure,
                      timeout=timeout,
                      tenant_id=tenant_id,
                      region_name=region_name,
                      endpoint_type=endpoint_type,
                      service_type=service_type,
                      service_name=service_name,
                      retries=retries,
                      http_log_debug=http_log_debug,
                      cacert=cacert,
                      bypass_url=bypass_url,
                      auth_system=auth_system,
                      auth_plugin=auth_plugin,
                      http_log_to_stream=http_log_to_stream,
                      )


class Client(object):
    """Top-level object to access the OpenStack Database API.

    Create an instance with your creds::

        >> client = Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)

    Then call methods on its managers::

        >> client.instances.list()
        ...

    """

    def __init__(self,
                 username,
                 password,
                 project_id=None,
                 auth_url=None,
                 insecure=False,
                 timeout=None,
                 tenant_id=None,
                 region_name=None,
                 endpoint_type=None,
                 extensions=None,
                 service_type='rax:database',
                 service_name='cloudDatabases',
                 retries=None,
                 http_log_debug=False,
                 cacert=None,
                 bypass_url=None,
                 auth_system='keystone',
                 auth_plugin=None,
                 session=None,
                 auth=None,
                 client_cls=None):

        # Load all extensions
        self.extensions = extensions or self.discover_extensions()

        # Add in extensions
        for extension in self.extensions:
            if extension.manager_class:
                setattr(self, extension.name, extension.manager_class(self))

        self.client = _construct_http_client(
            username=username,
            password=password,
            project_id=project_id,
            auth_url=auth_url,
            insecure=insecure,
            timeout=timeout,
            tenant_id=tenant_id,
            region_name=region_name,
            endpoint_type=endpoint_type,
            service_type=service_type,
            service_name=service_name,
            retries=retries,
            http_log_debug=http_log_debug,
            cacert=cacert,
            bypass_url=bypass_url,
            auth_system=auth_system,
            client_cls=client_cls)

    def authenticate(self):
        """Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`exceptions.Unauthorized` if the
        credentials are wrong.
        """
        self.client.authenticate()

    @classmethod
    def discover_extensions(cls):
        extensions = []
        for name, module in cls._discover_via_entry_points():
            extension = Extension(name, module)
            extensions.append(extension)

        return extensions

    @classmethod
    def _discover_via_entry_points(cls):
        for ep in pkg_resources.iter_entry_points('cdbclient.extension'):
            name = ep.name
            module = ep.load()

            yield name, module
