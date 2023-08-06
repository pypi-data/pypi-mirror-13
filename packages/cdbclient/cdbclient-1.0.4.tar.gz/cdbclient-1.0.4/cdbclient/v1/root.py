# Copyright 2011 OpenStack Foundation
# Copyright 2013 Rackspace Hosting
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

from cdbclient import base
from cdbclient import common
from cdbclient import utils
from cdbclient.v1 import users


class Root(base.ManagerWithFind):
    """Manager class for Root resource."""
    resource_class = users.User
    url = "/instances/%s/root"

    def create(self, instance_id):
        """Implements root-enable API.

        Enable the root user and return the root password for the
        specified db instance.
        """
        resp, body = self.api.client.post(self.url % instance_id)
        common.check_for_exceptions(resp, body, self.url)
        return body['user']['name'], body['user']['password']

    def is_root_enabled(self, instance_id):
        """Return whether root is enabled for the instance."""
        resp, body = self.api.client.get(self.url % instance_id)
        common.check_for_exceptions(resp, body, self.url)
        return self.resource_class(self, body, loaded=True)

    # Appease the abc gods
    def list(self):
        pass


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
def do_root_enable(cs, args):
    """Enables root for an instance and resets if already exists."""
    root = cs.root.create(args.instance)
    utils.print_dict({'name': root[0], 'password': root[1]})


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
def do_root_show(cs, args):
    """Gets status if root was ever enabled for an instance."""
    root = cs.root.is_root_enabled(args.instance)
    utils.print_dict({'is_root_enabled': root.rootEnabled})
