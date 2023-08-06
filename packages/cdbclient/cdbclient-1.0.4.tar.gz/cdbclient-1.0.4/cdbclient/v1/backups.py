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
from cdbclient import common
from cdbclient import utils
from cdbclient import exceptions


class Backup(base.Resource):
    """Backup is a resource used to hold backup information."""
    def __repr__(self):
        return "<Backup: %s>" % self.name


class Backups(base.ManagerWithFind):
    """Manage :class:`Backups` information."""

    resource_class = Backup

    def get(self, backup):
        """Get a specific backup.

        :rtype: :class:`Backups`
        """
        return self._get("/backups/%s" % base.getid(backup),
                         "backup")

    def list(self, limit=None, marker=None, datastore=None):
        """Get a list of all backups.

        :rtype: list of :class:`Backups`.
        """
        query_strings = {}
        if datastore:
            query_strings = {'datastore': datastore}

        return self._paginated("/backups", "backups", limit, marker,
                               query_strings)

    def create(self, name, instance=None, description=None, parent_id=None,
               backup=None, backup_type=None, is_automated=False,
               ha_instance=None):
        """Create a new backup from the given instance."""
        body = {
            "backup": {
                "name": name,
                "instance": None
            }
        }

        if instance:
            body['backup']['instance'] = base.getid(instance)
        if ha_instance:
            source = {"id": base.getid(ha_instance), "type": "ha"}
            body['backup']['source'] = source
        if backup:
            body["backup"]['backup'] = backup
        if description:
            body['backup']['description'] = description
        if parent_id:
            body['backup']['parent_id'] = parent_id
        if backup_type:
            body['backup']['backup_type'] = backup_type
        body['backup']['is_automated'] = is_automated
        return self._create("/backups", body, "backup")

    def delete(self, backup_id):
        """Delete the specified backup.

        :param backup_id: The backup id to delete
        """
        url = "/backups/%s" % base.getid(backup_id)
        resp, body = self.api.client.delete(url)
        common.check_for_exceptions(resp, body, url)


@utils.arg('backup', metavar='<backup>', help='ID of the backup.')
def do_backup_show(cs, args):
    """Shows details of a backup."""
    backup = utils.find_resource(cs.backups, args.backup)
    utils.print_object(backup)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('--limit', metavar='<limit>',
           default=None,
           help='Return up to N number of the most recent backups.')
def do_backup_list_instance(cs, args):
    """Lists available backups for an instance."""
    instance = utils.find_resource(cs.instances, args.instance)
    wrapper = cs.instances.backups(instance, limit=args.limit)
    backups = wrapper.items
    while wrapper.next and not args.limit:
        wrapper = cs.instances.backups(args.instance, marker=wrapper.next)
        backups += wrapper.items
    utils.print_list(backups, ['id', 'name', 'status',
                               'parent_id', 'updated'],
                     order_by='updated')


@utils.arg('--limit', metavar='<limit>',
           default=None,
           help='Return up to N number of the most recent backups.')
@utils.arg('--datastore', metavar='<datastore>',
           default=None,
           help='Name or ID of the datastore to list backups for.')
def do_backup_list(cs, args):
    """Lists available backups."""
    wrapper = cs.backups.list(limit=args.limit, datastore=args.datastore)
    backups = wrapper.items
    while wrapper.next and not args.limit:
        wrapper = cs.backups.list(marker=wrapper.next)
        backups += wrapper.items
    for backup in backups:
        if backup.source.get("type") == "ha":
          setattr(backup, 'ha_id', backup.source.get("id"))
    utils.print_list(backups, ['id', 'instance_id', 'name',
                               'status', 'parent_id', 'type', 'updated',
                               'ha_id'],
                     order_by='updated')


@utils.arg('backup', metavar='<backup>', help='ID of the backup.')
def do_backup_delete(cs, args):
    """Deletes a backup."""
    backup = utils.find_resource(cs.backups, args.backup)
    cs.backups.delete(backup)


@utils.arg('name', metavar='<name>', help='Name of the backup.')
@utils.arg('--instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('--ha_instance', metavar='<ha_instance>', help='ID of the HA instance.')
@utils.arg('--description', metavar='<description>',
           default=None,
           help='An optional description for the backup.')
@utils.arg('--parent', metavar='<parent>', default=None,
           help='Optional ID of the parent backup to perform an'
           ' incremental backup from.')
@utils.arg('--type', metavar='<type>', default=None,
           help='Type of backup.')
def do_backup_create(cs, args):
    """Creates a backup of an instance/HA instance."""
    if (args.instance is None and
        args.ha_instance is None):
        err_msg = ("Specify either an instance or HA instance id."
                   "$trove help backup-create")
        raise exceptions.CommandError(err_msg)
    if (args.instance and args.ha_instance):
        err_msg = ("Specify either an instance or HA instance id."
                   "$trove help backup-create")
        raise exceptions.CommandError(err_msg)
    backup = cs.backups.create(args.name,
                               instance=args.instance,
                               ha_instance=args.ha_instance,
                               description=args.description,
                               parent_id=args.parent,
                               backup_type=args.type)
    utils.print_object(backup)
