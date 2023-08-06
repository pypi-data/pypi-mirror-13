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
from cdbclient.v1 import databases


class User(base.Resource):
    """A database user."""
    def __repr__(self):
        return "<User: %s>" % self.name


class Users(base.ManagerWithFind):
    """Manage :class:`Users` resources."""
    resource_class = User

    def create(self, instance_id, users):
        """Create users with permissions to the specified databases."""
        body = {"users": users}
        url = "/instances/%s/users" % instance_id
        resp, body = self.api.client.post(url, body=body)
        common.check_for_exceptions(resp, body, url)

    def delete(self, instance_id, username, hostname=None):
        """Delete an existing user in the specified instance."""
        user = common.quote_user_host(username, hostname)
        url = "/instances/%s/users/%s" % (instance_id, user)
        resp, body = self.api.client.delete(url)
        common.check_for_exceptions(resp, body, url)

    def list(self, instance, limit=None, marker=None):
        """Get a list of all Users from the instance's Database.

        :rtype: list of :class:`User`.
        """
        url = "/instances/%s/users" % base.getid(instance)
        return self._paginated(url, "users", limit, marker)

    def get(self, instance_id, username, hostname=None):
        """Get a single User from the instance's Database.

        :rtype: :class:`User`.
        """
        user = common.quote_user_host(username, hostname)
        url = "/instances/%s/users/%s" % (instance_id, user)
        return self._get(url, "user")

    def update_attributes(self, instance, username, newuserattr=None,
                          hostname=None):
        """Update attributes of a single User in an instance.

        :rtype: :class:`User`.
        """
        if not newuserattr:
            raise Exception("No updates specified for user %s" % username)
        instance_id = base.getid(instance)
        user = common.quote_user_host(username, hostname)
        user_dict = {}
        user_dict['user'] = newuserattr
        url = "/instances/%s/users/%s" % (instance_id, user)
        resp, body = self.api.client.put(url, body=user_dict)
        common.check_for_exceptions(resp, body, url)

    def list_access(self, instance, username, hostname=None):
        """Show all databases the given user has access to."""
        instance_id = base.getid(instance)
        user = common.quote_user_host(username, hostname)
        url = "/instances/%(instance_id)s/users/%(user)s/databases"
        local_vars = locals()
        resp, body = self.api.client.get(url % local_vars)
        common.check_for_exceptions(resp, body, url)
        if not body:
            raise Exception("Call to %s did not return to a body" % url)
        return [databases.Database(self, db) for db in body['databases']]

    def grant(self, instance, username, databases, hostname=None):
        """Allow an existing user permissions to access a database."""
        instance_id = base.getid(instance)
        user = common.quote_user_host(username, hostname)
        url = "/instances/%(instance_id)s/users/%(user)s/databases"
        dbs = {'databases': [{'name': db} for db in databases]}
        local_vars = locals()
        resp, body = self.api.client.put(url % local_vars, body=dbs)
        common.check_for_exceptions(resp, body, url)

    def revoke(self, instance, username, database, hostname=None):
        """Revoke from an existing user access permissions to a database."""
        instance_id = base.getid(instance)
        user = common.quote_user_host(username, hostname)
        url = ("/instances/%(instance_id)s/users/%(user)s/"
               "databases/%(database)s")
        local_vars = locals()
        resp, body = self.api.client.delete(url % local_vars)
        common.check_for_exceptions(resp, body, url)

    def change_passwords(self, instance, users):
        """Change the password for one or more users."""
        instance_id = base.getid(instance)
        user_dict = {"users": users}
        url = "/instances/%s/users" % instance_id
        resp, body = self.api.client.put(url, body=user_dict)
        common.check_for_exceptions(resp, body, url)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('name', metavar='<name>', help='Name of user.')
@utils.arg('password', metavar='<password>', help='Password of user.')
@utils.arg('--host', metavar='<host>', default=None,
           help='Optional host of user.')
@utils.arg('--databases', metavar='<databases>',
           help='Optional list of databases.',
           nargs="+", default=[])
def do_user_create(cs, args):
    """Creates a user on an instance."""
    databases = [{'name': value} for value in args.databases]
    user = {'name': args.name, 'password': args.password,
            'databases': databases}
    if args.host:
        user['host'] = args.host
    cs.users.create(args.instance, [user])


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
def do_user_list(cs, args):
    """Lists the users for an instance."""
    wrapper = cs.users.list(args.instance)
    users = wrapper.items
    while (wrapper.next):
        wrapper = cs.users.list(args.instance, marker=wrapper.next)
        users += wrapper.items
    for user in users:
        db_names = [db['name'] for db in user.databases]
        user.databases = ', '.join(db_names)
    utils.print_list(users, ['name', 'host', 'databases'])


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('name', metavar='<name>', help='Name of user.')
@utils.arg('--host', metavar='<host>', default=None,
           help='Optional host of user.')
def do_user_delete(cs, args):
    """Deletes a user from an instance."""
    cs.users.delete(args.instance, args.name, hostname=args.host)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('name', metavar='<name>', help='Name of user.')
@utils.arg('--host', metavar='<host>', default=None,
           help='Optional host of user.')
def do_user_show(cs, args):
    """Shows details of a user of an instance."""
    user = cs.users.get(args.instance, args.name, hostname=args.host)
    utils.print_object(user)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('name', metavar='<name>', help='Name of user.')
@utils.arg('--host', metavar='<host>', default=None,
           help='Optional host of user.')
def do_user_show_access(cs, args):
    """Shows access details of a user of an instance."""
    access = cs.users.list_access(args.instance, args.name, hostname=args.host)
    utils.print_list(access, ['name'])


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('name', metavar='<name>', help='Name of user.')
@utils.arg('--host', metavar='<host>', default=None,
           help='Optional host of user.')
@utils.arg('--new_name', metavar='<new_name>', default=None,
           help='Optional new name of user.')
@utils.arg('--new_password', metavar='<new_password>', default=None,
           help='Optional new password of user.')
@utils.arg('--new_host', metavar='<new_host>', default=None,
           help='Optional new host of user.')
def do_user_update_attributes(cs, args):
    """Updates a user's attributes on an instance.
    At least one optional argument must be provided.
    """
    new_attrs = {}
    if args.new_name:
        new_attrs['name'] = args.new_name
    if args.new_password:
        new_attrs['password'] = args.new_password
    if args.new_host:
        new_attrs['host'] = args.new_host
    cs.users.update_attributes(args.instance, args.name,
                               newuserattr=new_attrs, hostname=args.host)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('name', metavar='<name>', help='Name of user.')
@utils.arg('--host', metavar='<host>', default=None,
           help='Optional host of user.')
@utils.arg('databases', metavar='<databases>',
           help='List of databases.',
           nargs="+", default=[])
def do_user_grant_access(cs, args):
    """Grants access to a database(s) for a user."""
    cs.users.grant(args.instance, args.name,
                   args.databases, hostname=args.host)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('name', metavar='<name>', help='Name of user.')
@utils.arg('database', metavar='<database>', help='A single database.')
@utils.arg('--host', metavar='<host>', default=None,
           help='Optional host of user.')
def do_user_revoke_access(cs, args):
    """Revokes access to a database for a user."""
    cs.users.revoke(args.instance, args.name,
                    args.database, hostname=args.host)
