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

from cdbclient import base
from cdbclient import utils


class Limit(base.Resource):

    def __repr__(self):
        return "<Limit: %s>" % self.verb


class Limits(base.ManagerWithFind):
    """Manages :class `Limit` resources."""
    resource_class = Limit

    def __repr__(self):
        return "<Limit Manager at %s>" % id(self)

    def list(self):
        """Retrieve the limits."""
        return self._list("/limits", "limits")


def do_limit_list(cs, args):
    """Lists the limits for a tenant."""
    limits = cs.limits.list()
    # Pop the first one, its absolute limits
    absolute = limits.pop(0)
    utils.print_object(absolute)
    utils.print_list(limits, ['value', 'verb', 'remaining', 'unit'])
