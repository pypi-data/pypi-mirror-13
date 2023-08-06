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

REBOOT_SOFT = 'SOFT'
REBOOT_HARD = 'HARD'


class Instance(base.Resource):
    """An Instance is an opaque instance used to store Database instances."""
    def __repr__(self):
        return "<Instance: %s>" % self.name

    def list_databases(self):
        return self.manager.databases.list(self)

    def delete(self):
        """Delete the instance."""
        self.manager.delete(self)

    def restart(self):
        """Restart the database instance."""
        self.manager.restart(self.id)

    def detach_replica(self):
        """Stops the replica database from being replicated to."""
        self.manager.edit(self.id, detach_replica_source=True)


class Instances(base.ManagerWithFind):
    """Manage :class:`Instance` resources."""
    resource_class = Instance

    # TODO(SlickNik): Remove slave_of param after updating tests to replica_of
    def create(self, name, flavor_id, volume=None, databases=None, users=None,
               restorePoint=None, availability_zone=None, datastore=None,
               datastore_version=None, configuration=None,
               replica_of=None, slave_of=None):
        """Create (boot) a new instance."""

        body = {"instance": {
            "name": name,
            "flavorRef": flavor_id
        }}
        datastore_obj = {}
        if volume:
            body["instance"]["volume"] = volume
        if databases:
            body["instance"]["databases"] = databases
        if users:
            body["instance"]["users"] = users
        if restorePoint:
            body["instance"]["restorePoint"] = restorePoint
        if availability_zone:
            body["instance"]["availability_zone"] = availability_zone
        if datastore:
            datastore_obj["type"] = datastore
        if datastore_version:
            datastore_obj["version"] = datastore_version
        if datastore_obj:
            body["instance"]["datastore"] = datastore_obj
        if configuration:
            body["instance"]["configuration"] = configuration
        if replica_of or slave_of:
            body["instance"]["replica_of"] = replica_of or slave_of

        return self._create("/instances", body, "instance")

    def modify(self, instance_id, configuration=None):
        body = {
            "instance": {
            }
        }
        if configuration is not None:
            body["instance"]["configuration"] = configuration
        url = "/instances/%s" % base.getid(instance_id)
        resp, body = self.api.client.put(url, body=body)
        common.check_for_exceptions(resp, body, url)

    def edit(self, instance_id, configuration=None, name=None,
             detach_replica_source=False, remove_configuration=False):
        body = {
            "instance": {
            }
        }
        if configuration and remove_configuration:
            raise Exception("Cannot attach and detach configuration "
                            "simultaneosly.")
        if remove_configuration:
            body["instance"]["configuration"] = None
        if configuration is not None:
            body["instance"]["configuration"] = configuration
        if name is not None:
            body["instance"]["name"] = name
        if detach_replica_source:
            # TODO(glucas): Remove slave_of after updating trove
            # (see trove.instance.service.InstanceController#edit)
            body["instance"]["slave_of"] = None
            body["instance"]["replica_of"] = None

        url = "/instances/%s" % instance_id
        resp, body = self.api.client.patch(url, body=body)
        common.check_for_exceptions(resp, body, url)

    def list(self, limit=None, marker=None, include_clustered=None,
             include_replicas=None, include_ha=None):
        """Get a list of all instances.

        :rtype: list of :class:`Instance`.
        """

        query_params = {}
        if include_clustered is not None:
            query_params['include_clustered'] = str(include_clustered)
        if include_replicas is not None:
            query_params['include_replicas'] = str(include_replicas)
        if include_ha is not None:
            query_params['include_ha'] = str(include_ha)

        return self._paginated("/instances", "instances", limit, marker,
                               query_params)

    def list_replicas(self, instance, limit=None, marker=None):
        """Get a list of all replicas of an instance.

        :rtype: list of :class:`Instance`.
        """
        url = "/instances/%s/replicas" % base.getid(instance)
        return self._paginated(url, "instances", limit, marker)

    def get(self, instance):
        """Get a specific instances.

        :rtype: :class:`Instance`
        """
        return self._get("/instances/%s" % base.getid(instance),
                         "instance")

    def backups(self, instance, limit=None, marker=None):
        """Get the list of backups for a specific instance.

        :rtype: list of :class:`Backups`.
        """
        url = "/instances/%s/backups" % base.getid(instance)
        return self._paginated(url, "backups", limit, marker)

    def delete(self, instance):
        """Delete the specified instance.

        :param instance_id: The instance id to delete
        """
        url = "/instances/%s" % base.getid(instance)
        resp, body = self.api.client.delete(url)
        common.check_for_exceptions(resp, body, url)

    def _action(self, instance_id, body):
        """Perform a server "action" -- reboot/rebuild/resize/etc."""
        url = "/instances/%s/action" % base.getid(instance_id)
        resp, body = self.api.client.post(url, body=body)
        common.check_for_exceptions(resp, body, url)
        if body:
            return self.resource_class(self, body, loaded=True)
        return body

    def resize_volume(self, instance_id, volume_size):
        """Resize the volume on an existing instances."""
        body = {"resize": {"volume": {"size": volume_size}}}
        self._action(instance_id, body)

    def resize_instance(self, instance_id, flavor_id):
        """Resizes an instance with a new flavor."""
        body = {"resize": {"flavorRef": flavor_id}}
        self._action(instance_id, body)

    def restart(self, instance_id):
        """Restart the database instance.

        :param instance_id: The :class:`Instance` (or its ID) to share onto.
        """
        body = {'restart': {}}
        self._action(instance_id, body)

    def configuration(self, instance):
        """Get a configuration on instances.

        :rtype: :class:`Instance`
        """
        return self._get("/instances/%s/configuration" % base.getid(instance),
                         "instance")

    def convert_to_ha(self, instance_id, name, networks=None, acls=None):
        """Converts the instance into a HA instance."""
        body = {"convert_to_ha": {"name": name}}
        if networks is not None:
          body['convert_to_ha'].update({"networks": networks})
        if acls is not None:
          acl_list = []  
          for acl in acls:
            acl_list.append({"address": acl})
          body['convert_to_ha'].update({"acls": acl_list})
        return self._action(instance_id, body)


class InstanceStatus(object):

    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    BUILD = "BUILD"
    FAILED = "FAILED"
    REBOOT = "REBOOT"
    RESIZE = "RESIZE"
    SHUTDOWN = "SHUTDOWN"
    RESTART_REQUIRED = "RESTART_REQUIRED"


@utils.arg('--limit', metavar='<limit>', type=int, default=None,
           help='Limit the number of results displayed.')
@utils.arg('--marker', metavar='<ID>', type=str, default=None,
           help='Begin displaying the results for IDs greater than the '
                'specified marker. When used with --limit, set this to '
                'the last ID displayed in the previous run.')
@utils.arg('--include-replicas', metavar='<include_replicas>',
           type=str, default=True, help="Include instances which are "
           "replicas (default 'true').")
@utils.arg('--include-ha', metavar='<include_ha>',
           type=str, default=True, help="Include instances which are "
           "part of a HA setup (default 'true').")
@utils.arg('--include-clustered', dest='include_clustered',
           action="store_true", default=False,
           help="Include instances that are part of a cluster "
                "(default false).")
def do_list(cs, args):
    """Lists all the instances."""
    instances = cs.instances.list(limit=args.limit,
                                  marker=args.marker,
                                  include_replicas=args.include_replicas,
                                  include_ha=args.include_ha,
                                  include_clustered=args.include_clustered)

    for instance in instances:
        instance._loaded = True
        setattr(instance, 'flavor_id', instance.flavor['id'])
        if hasattr(instance, 'volume'):
            setattr(instance, 'size', instance.volume['size'])
        if hasattr(instance, 'datastore'):
            if instance.datastore.get('version'):
                setattr(instance, 'datastore_version',
                        instance.datastore['version'])
            setattr(instance, 'datastore', instance.datastore['type'])
    utils.print_list(instances, ['id', 'name', 'datastore',
                                 'datastore_version', 'status',
                                 'flavor_id', 'size'])


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
@utils.arg('--limit', metavar='<limit>', type=int, default=None,
           help='Limit the number of results displayed.')
@utils.arg('--marker', metavar='<ID>', type=str, default=None,
           help='Begin displaying the results for IDs greater than the '
                'specified marker. When used with --limit, set this to '
                'the last ID displayed in the previous run.')
@utils.service_type('database')
def do_replica_list(cs, args):
    """Lists all replicas of the instance."""
    instances = cs.instances.list_replicas(args.instance, limit=args.limit,
                                           marker=args.marker)

    for instance in instances:
        setattr(instance, 'flavor_id', instance.flavor['id'])
        if hasattr(instance, 'volume'):
            setattr(instance, 'size', instance.volume['size'])
        if hasattr(instance, 'datastore'):
            if instance.datastore.get('version'):
                setattr(instance, 'datastore_version',
                        instance.datastore['version'])
            setattr(instance, 'datastore', instance.datastore['type'])
    utils.print_list(instances, ['id', 'name', 'datastore',
                                 'datastore_version', 'status',
                                 'flavor_id', 'size'])


@utils.arg('instance', metavar='<instance>',
           help='ID or name of the instance.')
def do_show(cs, args):
    """Shows details of an instance."""
    instance = utils.find_resource(cs.instances, args.instance)
    utils.print_instance(instance)


@utils.arg('instance', metavar='<instance>', help='ID of the instance.')
def do_delete(cs, args):
    """Deletes an instance."""
    try:
        instance = utils.find_resource(cs.instances, args.instance)
        cs.instances.delete(instance)
    except:
        cs.instances.delete(args.instance)



@utils.arg('instance',
           metavar='<instance>',
           type=str,
           help='UUID of the instance.')
@utils.arg('--name',
           metavar='<name>',
           type=str,
           default=None,
           help='Name of the instance.')
@utils.arg('--configuration',
           metavar='<configuration>',
           type=str,
           default=None,
           help='ID of the configuration reference to attach.')
@utils.arg('--detach-replica-source',
           dest='detach_replica_source',
           action="store_true",
           default=False,
           help='Detach the replica instance from its replication source.')
@utils.arg('--remove_configuration',
           dest='remove_configuration',
           action="store_true",
           default=False,
           help='Drops the current configuration reference.')
def do_update(cs, args):
    """Updates an instance: Edits name, configuration, or replica source."""
    cs.instances.edit(args.instance, args.configuration, args.name,
                      args.detach_replica_source, args.remove_configuration)


@utils.arg('name',
           metavar='<name>',
           type=str,
           help='Name of the instance.')
@utils.arg('flavor_id',
           metavar='<flavor_id>',
           help='Flavor of the instance.')
@utils.arg('--size',
           metavar='<size>',
           type=int,
           default=None,
           help="Size of the instance disk volume in GB. "
                "Required when volume support is enabled.")
@utils.arg('--databases', metavar='<databases>',
           help='Optional list of databases.',
           nargs="+", default=[])
@utils.arg('--users', metavar='<users>',
           help='Optional list of users in the form user:password.',
           nargs="+", default=[])
@utils.arg('--backup',
           metavar='<backup>',
           default=None,
           help='A backup ID.')
@utils.arg('--availability_zone',
           metavar='<availability_zone>',
           default=None,
           help='The Zone hint to give to nova.')
@utils.arg('--datastore',
           metavar='<datastore>',
           default=None,
           help='A datastore name or ID.')
@utils.arg('--datastore_version',
           metavar='<datastore_version>',
           default=None,
           help='A datastore version name or ID.')
@utils.arg('--configuration',
           metavar='<configuration>',
           default=None,
           help='ID of the configuration group to attach to the instance.')
@utils.arg('--replica_of',
           metavar='<source_id>',
           default=None,
           help='ID of an existing instance to replicate from.')
def do_create(cs, args):
    """Creates a new instance."""
    volume = None
    if args.size:
        volume = {"size": args.size}
    restore_point = None
    if args.backup:
        restore_point = {"backupRef": args.backup}
    databases = [{'name': value} for value in args.databases]
    users = [{'name': n, 'password': p, 'databases': databases} for (n, p) in
             [z.split(':')[:2] for z in args.users]]
    instance = cs.instances.create(args.name,
                                   args.flavor_id,
                                   volume=volume,
                                   databases=databases,
                                   users=users,
                                   restorePoint=restore_point,
                                   availability_zone=args.availability_zone,
                                   datastore=args.datastore,
                                   datastore_version=args.datastore_version,
                                   configuration=args.configuration,
                                   replica_of=args.replica_of)
    utils.print_instance(instance)


@utils.arg('instance',
           metavar='<instance>',
           type=str,
           help='ID of the instance.')
@utils.arg('flavor_id',
           metavar='<flavor_id>',
           help='New flavor of the instance.')
def do_resize_flavor(cs, args):
    """[DEPRECATED] Please use resize-instance instead."""
    do_resize_instance(cs, args)


@utils.arg('instance',
           metavar='<instance>',
           type=str,
           help='ID of the instance.')
@utils.arg('flavor_id',
           metavar='<flavor_id>',
           help='New flavor of the instance.')
def do_resize_instance(cs, args):
    """Resizes an instance with a new flavor."""
    cs.instances.resize_instance(args.instance, args.flavor_id)


@utils.arg('instance',
           metavar='<instance>',
           type=str,
           help='ID of the instance.')
@utils.arg('size',
           metavar='<size>',
           type=int,
           default=None,
           help='New size of the instance disk volume in GB.')
def do_resize_volume(cs, args):
    """Resizes the volume size of an instance."""
    cs.instances.resize_volume(args.instance, args.size)


@utils.arg('instance',
           metavar='<instance>',
           type=str,
           help='ID of the instance.')
def do_restart(cs, args):
    """Restarts an instance."""
    cs.instances.restart(args.instance)


@utils.arg('instance',
           metavar='<instance>',
           type=str,
           help='ID of the instance.')
def do_detach_replica(cs, args):
    """Detaches a replica instance from its replication source."""
    cs.instances.edit(args.instance, detach_replica_source=True)


@utils.arg('instance',
           metavar='<instance>',
           type=str,
           help='ID of the instance.')
@utils.arg('configuration',
           metavar='<configuration>',
           type=str,
           help='ID of the configuration group to attach to the instance.')
def do_configuration_attach(cs, args):
    """Attaches a configuration group to an instance."""
    cs.instances.modify(args.instance, args.configuration)


@utils.arg('instance',
           metavar='<instance>',
           type=str,
           help='ID of the instance.')
def do_configuration_detach(cs, args):
    """Detaches a configuration group from an instance."""
    cs.instances.modify(args.instance)


@utils.arg('instance',
           metavar='<instance>',
           type=str,
           help='ID of the instance.')
@utils.arg('name',
           metavar='<name>',
           type=str,
           help='Name of the HA instance.')
@utils.arg('--networks', metavar='<networks>',
           default=None,
           help=('Comma-separated list of networks, consisting of '
                 'public and/or servicenet'))
@utils.arg('--acls', metavar='<acls>',
           default=None,
           help=('Comma-separated list of acls'))
def do_convert_to_ha(cs, args):
    """Converts the instance into HA instance"""
    networks = args.networks
    if networks is not None:
        networks = networks.split(',')
    acls = args.acls
    if acls is not None:
        acls = acls.split(',')
    ha_instance = cs.instances.convert_to_ha(args.instance, args.name,
                                             networks=networks,
                                             acls=acls)
    info = ha_instance.__dict__['_info']
    ha_info = info['ha_instance']
    datastore = ha_info.pop('datastore', {})
    dsv = datastore.get('version')
    ds = datastore.get('type')
    ha_info['datastore'] = '%s - %s' % (ds, dsv)
    if ha_info.get('replica_source'):
        source = [rs['id'] for rs in ha_info['replica_source']]
        ha_info['replica_source'] = ', '.join(source)
    if ha_info.get('replicas'):
        replicas = [replica['id'] for replica in ha_info['replicas']]
        ha_info['replicas'] = ', '.join(replicas)
    utils.print_dict(ha_info)
