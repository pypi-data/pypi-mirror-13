
import urlparse

from cdbclient import base
from cdbclient import utils
from cdbclient import common
from cdbclient.common import check_for_exceptions
from cdbclient import exceptions


class HA(base.Resource):
    """
    An HA Instance  resource.
    """
    def __repr__(self):
        return "<ha: %s>" % getattr(self, 'id')


class HAManager(base.Manager):
    """
    Manage :class:`HA` resources.
    """
    resource_class = HA

    def create(self, name, datastore, replica_source, replicas,
               networks=None, acls=None):
        """
        Create an HA instance
        Request:
        {
            "ha" : {
                "replica_source": [
                    {
                         "flavorRef" : 9,
                         "volume" : {"size" : 1},
                         "name" : "rsource"
                    }
                ],
                "replicas": [
                    {
                        "flavorRef" : 9,
                        "volume" : {"size": 1"},
                        "name" : "replica-1"
                    },
                    {
                        "flavorRef" : 9,
                        "volume" : {"size": 1"},
                        "name" : "replica-1"
                    },
                ],
        "datastore" : {
                        "version" : 5.6,
                        "type" : "MYSQL"
                      },
        "networks" : ["servicenet", "publicnet"],
        "acls" : [],
        "name" : "HA-1",
        }

        :rtype: :class:`HA`
        """
        acl_list = []
        if acls:   
            for acl in acls:
                acl_list.append({"address": acl})
 
        body = {
            "ha": {
                "name": name,
                "datastore": datastore,
                "replica_source": replica_source,
                "replicas": replicas,
                "networks": networks or [],
                "acls": acl_list
            }
        }

        return self._create("/ha", body, "ha_instance")

    def delete(self, ha_instance_id):
        """
        Delete a specific HA Instance
        """
        return self._delete("/ha/%s" % ha_instance_id)

    def list(self, limit=None, marker=None):
        """
        Get a list of all HAInstances for an account.

        :rtype: list of :class:`HAInstance`.
        """
        return self._paginated("/ha", "ha_instances", limit, marker)

    def show(self, ha_instance_id):
        """
        Get a specific HA instance.

        :rtype: :class:`HAInstance`
        """
        return self._get("/ha/%s" % ha_instance_id, "ha_instance")

    def mgmt_list(self, limit=None, marker=None, deleted=None, tenant=None):
        """
        Get a list of all HAInstances for an account.

        :rtype: list of :class:`HAInstance`.
        """
        return self._paginated("/mgmt/ha", "ha_instances", limit, marker,
                               {"deleted": deleted, "tenant": tenant})

    def add_acl(self, ha_id, acl):
        """
        Add an ACL for an HA instance.
        """
        url = "/ha/{0}/acls".format(ha_id)
        body = {"address": acl}
        resp, body = self.api.client.post(url, body=body)
        common.check_for_exceptions(resp, body, url)

    def add_acls(self, ha_id, acl_list):
        """
        Add a list of ACLs for an HA instance.
        """
        url = "/ha/{0}/action".format(ha_id)
        body_post = {'add_acls': {'addresses': acl_list}}
        resp, body = self.api.client.post(url, body=body_post)
        common.check_for_exceptions(resp, body, url)

    def remove_acl(self, ha_id, acl):
        """
        Remove an ACL from an HA instance.
        """
        # Double encode slashes to get by both repose and trove routing.
        # This is decoded in the api call.
        acl = acl.replace('/', '%25252F')
        url = "/ha/{0}/acls/{1}".format(ha_id, acl)
        resp, body = self.api.client.delete(url)
        common.check_for_exceptions(resp, body, url)

    def remove_acls(self, ha_id, acl_list):
        """
        Remove a list of ACLs for an HA instance.
        """
        url = "/ha/{0}/action".format(ha_id)
        body_post = {'delete_acls': {'addresses': acl_list}}
        resp, body = self.api.client.post(url, body=body_post)
        common.check_for_exceptions(resp, body, url)

    def list_acl(self, ha_id):
        """
        List ACLs for an HA instance
        """
        url = "/ha/%s/acls" % ha_id
        resp, body = self.api.client.get(url)
        common.check_for_exceptions(resp, body, url)
        return body['acls']

    def _action(self, ha_instance_id, body):
        """
        Performs action on a HA-MySQL instance.
        For eg: add-replica to existing setup.

        """
        url = "/ha/%s/action" % ha_instance_id
        resp, body = self.api.client.post(url, body=body)
        common.check_for_exceptions(resp, body, url)
        if body:
            return self.resource_class(self, body, loaded=True)
        return body

    def add_replica(self, ha_instance_id, replica_details):
        """
        Adds a replica node to an existing HA-MySQL setup.
        """
        body = {"add_replica": {"replica_details": replica_details}}
        self._action(ha_instance_id, body)

    def resize_volumes(self, ha_instance_id, volume_size):
        """
        Resize all volumes across an HA setup
        """
        body = {"resize_volumes": {"size": volume_size}}
        self._action(ha_instance_id, body)

    def remove_replica(self, ha_instance_id, instance_id):
        """
        Removes a replica node to an existing HA-MySQL setup.
        """
        self._action(ha_instance_id, {'remove_replica': instance_id})

    def resize_flavor(self, ha_instance_id, flavor):
        """ Resize an HA  instance to a new flavor """
        self._action(ha_instance_id, {'resize_flavor': flavor})

    def backups(self, ha_instance, limit=None, marker=None):
        """Get the list of backups for a specific HA instance.

        :rtype: list of :class:`Backups`.
        """
        url = "/ha/%s/backups" % base.getid(ha_instance)
        return self._paginated(url, "backups", limit, marker)


def show_ha_instance(ha_instance):
    info = ha_instance._info.copy()
    datastore = info.pop('datastore', {})
    dsv = datastore.get('version')
    ds = datastore.get('type')
    info['datastore'] = '%s - %s' % (ds, dsv)
    if hasattr(ha_instance, 'replica_source'):
        source = [rs['id'] for rs in ha_instance.replica_source]
        info['replica_source'] = ', '.join(source)
    if hasattr(ha_instance, 'replicas'):
        replicas = [replica['id'] for replica in ha_instance.replicas]
        info['replicas'] = ', '.join(replicas)
    if hasattr(ha_instance, 'flavor'):
        info.pop('flavor')
        info['flavor'] = ha_instance.flavor['id']
    if hasattr(ha_instance, 'volume'):
        info['volume_size'] = ha_instance.volume['size']
        info.pop('volume')
    utils.print_dict(info)


@utils.service_type('database')
@utils.arg('--name',
           metavar='<name>',
           type=str,
           help='Name of the HA MySQL instance.')
@utils.arg('--source_name',
           metavar='<source_name>',
           type=str,
           help='Name of the replica source instance.')
@utils.arg('--source_flavor_id',
           metavar='<source_flavor_id>',
           help='Flavor of the replica source instance.')
@utils.arg('--source_size',
           metavar='<source_size>',
           type=int,
           help="Size of the replica source instance disk volume"
                "in GB.")
@utils.arg('--number_of_replicas',
           metavar='<number_of_replicas>',
           type=int,
           help="Number of replicas of the source instance.")
@utils.arg('--networks', metavar='<networks>',
           default=None,
           help=('Comma-separated list of networks, consisting of '
                 'public and/or servicenet'))
@utils.arg('--acls', metavar='<acls>',
           default=None,
           help=('Comma-separated list of acls'))
def do_ha_mysql_create(cs, args):
    """Creates a HA MySQL instance."""
    datastore = {"version": "5.6", "type": "MYSQL"}

    if (args.name is None or
        args.source_name is None or
        args.source_flavor_id is None or
        args.source_size is None or
        args.number_of_replicas is None):
        err_msg = ("Missing Arguments. Specify name, source_name,"
                   " source_flavor_id, source_size, number_of_replicas.\n"
                   "$trove help ha-mysql-create")
        raise exceptions.CommandError(err_msg)

    replica_source = [{"name":args.source_name,
                       "flavorRef": args.source_flavor_id,
                       "volume": {"size": args.source_size}}]
    replicas = []
    for r in range(args.number_of_replicas):
        replicas.append({"name":args.source_name + "_replica" + str(r+1),
                         "flavorRef": args.source_flavor_id,
                         "volume": {"size": args.source_size}})

    networks = args.networks
    if networks is not None:
        networks = networks.split(',')
    acls = args.acls
    if acls is not None:
        acls = acls.split(',')

    resource = HAManager(cs)
    ha = resource.create(args.name, datastore, replica_source, replicas,
               networks=networks, acls=acls)
    utils.print_dict(ha._info)


@utils.arg('--limit', metavar='<limit>', type=int, default=None,
           help='Limit the number of results displayed.')
@utils.arg('--marker', metavar='<ID>', type=int, default=None,
           help='Begin displaying the results for IDs greater than the '
                'specified marker. When used with --limit, set this to '
                'the last ID displayed in the previous run.')
@utils.service_type('database')
def do_ha_mysql_list(cs, args):
    """List all the HA MySQL Instances."""
    resource = HAManager(cs)
    ha_instances = resource.list(limit=args.limit, marker=args.marker)
    for instance in ha_instances:
        if hasattr(instance, 'datastore'):
            if instance.datastore.get('version'):
                setattr(instance, 'datastore_version',
                        instance.datastore['version'])
            setattr(instance, 'datastore', instance.datastore['type'])
    utils.print_list(ha_instances, ['id', 'name', 'datastore',
                                    'datastore_version', 'state'])


@utils.service_type('database')
@utils.arg('instance', metavar='<ha_instance>', help='ID of the HA instance.')
def do_ha_mysql_show(cs, args):
    """Show details of a single HA MySQL Instance."""
    resource = HAManager(cs)
    ha_instance = resource.show(args.instance)

    show_ha_instance(ha_instance)


@utils.service_type('database')
@utils.arg('instance', metavar='<instance>', help='ID of the HA MySQL instance.')
def do_ha_mysql_delete(cs, args):
    """Delete a HA MySQL Instance."""
    resource = HAManager(cs)
    resource.delete(args.instance)


@utils.service_type('database')
@utils.arg('ha_instance', metavar='<ha_instance>', help='ID of the HA MySQL instance.')
@utils.arg('--replica_name',
           metavar='<replica_name>',
           type=str,
           help='Name of the replica instance.')
@utils.arg('--replica_flavor_id',
           metavar='<replica_flavor_id>',
           help='Flavor of the replica instance.')
@utils.arg('--replica_size',
           metavar='<replica_size>',
           type=int,
           help="Size of the replica instance disk volume"
                "in GB.")
def do_ha_mysql_add_replica(cs, args):
    """Adds a replica node to an existing HA-MySQL setup."""

    if (args.replica_name is None or
        args.replica_flavor_id is None or
        args.replica_size is None):
        err_msg = ("Missing Arguments. Specify replica_name, replica_flavor_id,"
                   " replica_size.\n"
                   "$trove help ha-mysql-add-replica")
        raise exceptions.CommandError(err_msg)

    replica_details = {"name":args.replica_name,
                       "flavorRef": args.replica_flavor_id,
                       "volume": {"size": args.replica_size}}

    resource = HAManager(cs)
    resource.add_replica(args.ha_instance, replica_details)


@utils.arg('ha_instance', metavar='<ha_instance>', help='ID of the HA MySQL instance.')
@utils.arg('instance', metavar='<instance>', help='ID of the replica.')
def do_ha_mysql_remove_replica(cs, args):
    """Removes a replica node from an existing HA-MySQL setup."""
    resource = HAManager(cs)
    resource.remove_replica(args.ha_instance, args.instance)


@utils.arg('instance', metavar='<ha_instance>', help='ID of the HA instance.')
@utils.arg('size',
           metavar='<size>',
           type=int,
           default=None,
           help='New size of the instance disk volume in GB.')
def do_ha_mysql_resize_volumes(cs, args):
    """Resize volumes across the HA cluster"""
    resource = HAManager(cs)
    resource.resize_volumes(args.instance, args.size)


@utils.arg('ha_instance', metavar='<ha_instance>', help='ID of the HA MySQL instance.')
@utils.arg('--limit', metavar='<limit>', default=None,
           help='Return up to N number of the most recent backups.')
@utils.service_type('database')
def do_ha_mysql_backup_list(cs, args):
    """List the available backups of a HA-MySQL Instance."""
    resource = HAManager(cs)
    wrapper = resource.backups(args.ha_instance, limit=args.limit)
    backups = wrapper.items
    while wrapper.next and not args.limit:
        wrapper = resource.backups(args.ha_instance, marker=wrapper.next)
        backups += wrapper.items
    utils.print_list(backups, ['id', 'name', 'status',
                               'parent_id', 'updated'],
                     order_by='updated')


@utils.arg('ha_instance', metavar='<ha_instance>', help='ID of the HA MySQL instance.')
@utils.arg('flavor_id', metavar='<flavor_id>', help='New flavor of the instance.')
@utils.service_type('database')
def do_ha_mysql_resize_flavor(cs, args):
    """Resize flavor across the HA cluster"""
    resource = HAManager(cs)
    resource.resize_flavor(args.ha_instance, args.flavor_id)
