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


class Database(base.Resource):
    """Wikipedia definition for database.

    "A database is a system intended to organize, store, and retrieve large
    amounts of data easily."
    """
    def __repr__(self):
        return "<Database: %s>" % self.name


class Databases(base.ManagerWithFind):
    """Manage :class:`Databases` resources."""
    resource_class = Database

    def create(self, instance_id, databases):
        """Create new databases within the specified instance."""
        body = {"databases": databases}
        url = "/instances/%s/databases" % instance_id
        resp, body = self.api.client.post(url, body=body)
        common.check_for_exceptions(resp, body, url)

    def delete(self, instance_id, dbname):
        """Delete an existing database in the specified instance."""
        url = "/instances/%s/databases/%s" % (instance_id, dbname)
        resp, body = self.api.client.delete(url)
        common.check_for_exceptions(resp, body, url)

    def list(self, instance, limit=None, marker=None):
        """Get a list of all Databases from the instance.

        :rtype: list of :class:`Database`.
        """
        url = "/instances/%s/databases" % base.getid(instance)
        return self._paginated(url, "databases", limit, marker)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('name', metavar='<name>', help='Name of the database.')
@utils.arg('--character_set', metavar='<character_set>',
           default=None,
           help='Optional character set for database.')
@utils.arg('--collate', metavar='<collate>', default=None,
           help='Optional collation type for database.')
def do_database_create(cs, args):
    """Creates a database on an instance."""
    database_dict = {'name': args.name}
    if args.collate:
        database_dict['collate'] = args.collate
    if args.character_set:
        database_dict['character_set'] = args.character_set
    cs.databases.create(args.instance,
                        [database_dict])


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
def do_database_list(cs, args):
    """Lists available databases on an instance."""
    wrapper = cs.databases.list(args.instance)
    databases = wrapper.items
    while (wrapper.next):
        wrapper = cs.databases.list(args.instance, marker=wrapper.next)
        databases += wrapper.items

    utils.print_list(databases, ['name'])


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('database', metavar='<database>', help='Name of the database.')
def do_database_delete(cs, args):
    """Deletes a database from an instance."""
    cs.databases.delete(args.instance, args.database)
