# Copyright 2011 OpenStack Foundation
# Copyright 2013 Mirantis, Inc.
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


class Datastore(base.Resource):

    def __repr__(self):
        return "<Datastore: %s>" % self.name


class Datastores(base.ManagerWithFind):
    """Manage :class:`Datastore` resources."""
    resource_class = Datastore

    def __repr__(self):
        return "<Datastore Manager at %s>" % id(self)

    def list(self, limit=None, marker=None):
        """Get a list of all datastores.

        :rtype: list of :class:`Datastore`.
        """
        return self._paginated("/datastores", "datastores", limit, marker)

    def get(self, datastore):
        """Get a specific datastore.

        :rtype: :class:`Datastore`
        """
        return self._get("/datastores/%s" % base.getid(datastore),
                         "datastore")


def do_datastore_list(cs, args):
    """Lists available datastores."""
    datastores = cs.datastores.list()
    utils.print_list(datastores, ['id', 'name'])


@utils.arg('datastore', metavar='<datastore>',
           help='ID of the datastore.')
def do_datastore_show(cs, args):
    """Shows details of a datastore."""
    datastore = cs.datastores.get(args.datastore)
    if hasattr(datastore, 'default_version'):
        datastore._info['default_version'] = getattr(datastore,
                                                     'default_version')
    utils.print_object(datastore)
