# Copyright (c) 2014 OpenStack, LLC.
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


import json
from cdbclient import base
from cdbclient import common
from cdbclient import utils


class Configuration(base.Resource):
    """Configuration is a resource used to hold configuration information."""
    def __repr__(self):
        return "<Configuration: %s>" % self.name


class Configurations(base.ManagerWithFind):
    """Manage :class:`Configurations` information."""

    resource_class = Configuration

    def get(self, configuration):
        """Get a specific configuration.

        :rtype: :class:`Configurations`
        """
        return self._get("/configurations/%s" % base.getid(configuration),
                         "configuration")

    def instances(self, configuration, limit=None, marker=None):
        """Get a list of instances on a configuration.

        :rtype: :class:`Configurations`
        """
        return self._list("/configurations/%s/instances" %
                          base.getid(configuration),
                          "instances", limit, marker)

    def list(self, limit=None, marker=None):
        """Get a list of all configurations.

        :rtype: list of :class:`Configurations`.
        """
        return self._paginated("/configurations", "configurations",
                               limit, marker)

    def create(self, name, values, description=None, datastore=None,
               datastore_version=None):
        """Create a new configuration."""
        body = {
            "configuration": {
                "name": name,
                "values": json.loads(values)
            }
        }
        datastore_obj = {}
        if datastore:
            datastore_obj["type"] = datastore
        if datastore_version:
            datastore_obj["version"] = datastore_version
        if datastore_obj:
            body["configuration"]["datastore"] = datastore_obj
        if description:
            body['configuration']['description'] = description
        return self._create("/configurations", body, "configuration")

    def update(self, configuration_id, values, name=None, description=None):
        """Update an existing configuration."""
        body = {
            "configuration": {
                "values": json.loads(values)
            }
        }
        if name:
            body['configuration']['name'] = name
        if description:
            body['configuration']['description'] = description
        url = "/configurations/%s" % configuration_id
        resp, body = self.api.client.put(url, body=body)
        common.check_for_exceptions(resp, body, url)

    def edit(self, configuration_id, values):
        """Update an existing configuration."""
        body = {
            "configuration": {
                "values": json.loads(values)
            }
        }
        url = "/configurations/%s" % configuration_id
        resp, body = self.api.client.patch(url, body=body)
        common.check_for_exceptions(resp, body, url)

    def delete(self, configuration_id):
        """Delete the specified configuration.

        :param configuration_id: The configuration id to delete
        """
        url = "/configurations/%s" % configuration_id
        resp, body = self.api.client.delete(url)
        common.check_for_exceptions(resp, body, url)

    def default(self, datastore_version, flavor):
        """Get the default configuration for a version/flavor combo.

        :rtype: :class:`Configurations`
        """
        return self._get("/datastore/version/%s/configuration/%s" %
                         (datastore_version, flavor))


@utils.arg('name', metavar='<name>', help='Name of the configuration group.')
@utils.arg('values', metavar='<values>',
           help='Dictionary of the values to set.')
@utils.arg('--datastore', metavar='<datastore>',
           help='Datastore assigned to the configuration group.')
@utils.arg('--datastore_version', metavar='<datastore_version>',
           help='Datastore version ID assigned to the configuration group.')
@utils.arg('--description', metavar='<description>',
           default=None,
           help='An optional description for the configuration group.')
def do_configuration_create(cs, args):
    """Creates a configuration group."""
    config_grp = cs.configurations.create(
        args.name,
        args.values,
        description=args.description,
        datastore=args.datastore,
        datastore_version=args.datastore_version)
    config_grp._info['values'] = json.dumps(config_grp.values)
    utils.print_object(config_grp)


@utils.arg('instance',
           metavar='<instance>',
           type=str,
           help='ID of the instance.')
def do_configuration_default(cs, args):
    """Shows the default configuration of an instance."""
    configs = cs.instances.configuration(args.instance)
    utils.print_dict(configs._info['configuration'])


@utils.arg('configuration_group', metavar='<configuration_group>',
           help='ID of the configuration group.')
def do_configuration_delete(cs, args):
    """Deletes a configuration group."""
    cs.configurations.delete(args.configuration_group)


@utils.arg('configuration_group', metavar='<configuration_group>',
           help='ID of the configuration group.')
@utils.arg('values', metavar='<values>',
           help='Dictionary of the values to set.')
def do_configuration_patch(cs, args):
    """Patches a configuration group."""
    cs.configurations.edit(args.configuration_group,
                           args.values)


@utils.arg('configuration_group', metavar='<configuration_group>',
           help='ID of the configuration group.')
def do_configuration_instances(cs, args):
    """Lists all instances associated with a configuration group."""
    params = cs.configurations.instances(args.configuration_group)
    utils.print_list(params, ['id', 'name'])


def do_configuration_list(cs, args):
    """Lists all configuration groups."""
    config_grps = cs.configurations.list()
    utils.print_list(config_grps, [
        'id', 'name', 'description',
        'datastore_name', 'datastore_version_name'])


@utils.arg('configuration_group', metavar='<configuration_group>',
           help='ID of the configuration group.')
def do_configuration_show(cs, args):
    """Shows details of a configuration group."""
    config_grp = cs.configurations.get(args.configuration_group)
    config_grp._info['values'] = json.dumps(config_grp.values)
    utils.print_object(config_grp, remove=['datastore_version_id'])


@utils.arg('configuration_group', metavar='<configuration_group>',
           help='ID of the configuration group.')
@utils.arg('values', metavar='<values>',
           help='Dictionary of the values to set.')
@utils.arg('--name', metavar='<name>', default=None,
           help='Name of the configuration group.')
@utils.arg('--description', metavar='<description>',
           default=None,
           help='An optional description for the configuration group.')
def do_configuration_update(cs, args):
    """Updates a configuration group."""
    cs.configurations.update(args.configuration_group,
                             args.values,
                             args.name,
                             args.description)


@utils.arg('datastore_version',
           metavar='<datastore_version>',
           type=str,
           help='ID of the datastore version')
@utils.arg('flavor',
           metavar='<flavor>',
           type=str,
           help='ID of the flavor')
def do_configuration_default_dsversion_flavor(cs, args):
    """Shows the default configuration for a datastore version flavor."""
    configs = cs.configurations.default(args.datastore_version,
                                        args.flavor)
    utils.print_dict(configs._info['configuration'])
