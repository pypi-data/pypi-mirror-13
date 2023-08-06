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
from cdbclient import common
from cdbclient import exceptions
from cdbclient import utils


class DatastoreVersion(base.Resource):

    def __repr__(self):
        return "<DatastoreVersion: %s>" % self.name


class DatastoreVersions(base.ManagerWithFind):
    """Manage :class:`DatastoreVersion` resources."""
    resource_class = DatastoreVersion

    def __repr__(self):
        return "<DatastoreVersions Manager at %s>" % id(self)

    def list(self, datastore, limit=None, marker=None):
        """Get a list of all datastore versions.

        :rtype: list of :class:`DatastoreVersion`.
        """
        return self._paginated("/datastores/%s/versions" % datastore,
                               "versions", limit, marker)

    def get(self, datastore, datastore_version):
        """Get a specific datastore version.

        :rtype: :class:`DatastoreVersion`
        """
        return self._get("/datastores/%s/versions/%s" %
                         (datastore, base.getid(datastore_version)),
                         "version")

    def get_by_uuid(self, datastore_version):
        """Get a specific datastore version.

        :rtype: :class:`DatastoreVersion`
        """
        return self._get("/datastores/versions/%s" %
                         base.getid(datastore_version),
                         "version")

    def update(self, datastore, datastore_version_id, visibility):
        """Mgmt call to update a specific datastore version."""
        body = {
            "datastore_version": {
            }
        }
        if visibility is not None:
            body["datastore_version"]["visibility"] = visibility

        output = {
            'datastore': datastore,
            'datastore_version': datastore_version_id
        }

        url = ("/mgmt/datastores/%(datastore)s/"
               "versions/%(datastore_version)s" % output)
        resp, body = self.api.client.put(url, body=body)
        common.check_for_exceptions(resp, body, url)


@utils.arg('datastore', metavar='<datastore>',
           help='ID or name of the datastore.')
def do_datastore_version_list(cs, args):
    """Lists available versions for a datastore."""
    datastore_versions = cs.datastore_versions.list(args.datastore)
    utils.print_list(datastore_versions, ['id', 'name'])


@utils.arg('--datastore', metavar='<datastore>',
           default=None,
           help='ID or name of the datastore. Optional if the ID of the'
                ' datastore_version is provided.')
@utils.arg('datastore_version', metavar='<datastore_version>',
           help='ID or name of the datastore version.')
def do_datastore_version_show(cs, args):
    """Shows details of a datastore version."""
    if args.datastore:
        datastore_version = cs.datastore_versions.get(args.datastore,
                                                      args.datastore_version)
    elif utils.is_uuid_like(args.datastore_version):
        datastore_version = cs.datastore_versions.get_by_uuid(
            args.datastore_version)
    else:
        raise exceptions.NoUniqueMatch('The datastore name or id is required'
                                       ' to retrieve a datastore version'
                                       ' by name.')
    utils.print_object(datastore_version)
