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


from cdbclient import base
from cdbclient import common
from cdbclient import exceptions
from cdbclient import utils


class ConfigurationParameter(base.Resource):
    """Configuration Parameter."""
    def __repr__(self):
        return "<ConfigurationParameter: %s>" % self.__dict__


class ConfigurationParameters(base.Manager):
    """Manage :class:`ConfigurationParameters` information."""

    resource_class = ConfigurationParameter

    def parameters(self, datastore, version):
        """Get a list of valid parameters that can be changed."""
        return self._list("/datastores/%s/versions/%s/parameters" %
                          (datastore, version), "configuration-parameters")

    def get_parameter(self, datastore, version, key):
        """Get a list of valid parameters that can be changed."""
        return self._get("/datastores/%s/versions/%s/parameters/%s" %
                         (datastore, version, key))

    def parameters_by_version(self, version):
        """Get a list of valid parameters that can be changed."""
        return self._list("/datastores/versions/%s/parameters" % version,
                          "configuration-parameters")

    def get_parameter_by_version(self, version, key):
        """Get a list of valid parameters that can be changed."""
        return self._get("/datastores/versions/%s/parameters/%s" %
                         (version, key))

    def create(self, version, name, restart_required, data_type,
               max_size=None, min_size=None):
        """Mgmt call to create a new configuration parameter."""
        body = {
            "configuration-parameter": {
                "name": name,
                "restart_required": int(restart_required),
                "data_type": data_type,
            }
        }
        if max_size is not None:
            body["configuration-parameter"]["max_size"] = max_size
        if min_size is not None:
            body["configuration-parameter"]["min_size"] = min_size

        url = "/mgmt/datastores/versions/%s/parameters" % version
        resp, body = self.api.client.post(url, body=body)
        common.check_for_exceptions(resp, body, url)

    def list_all_parameter_by_version(self, version):
        """List all configuration parameters deleted or not."""
        return self._list("/mgmt/datastores/versions/%s/parameters" %
                          version, "configuration-parameters")

    def get_any_parameter_by_version(self, version, key):
        """Get any configuration parameter deleted or not."""
        return self._get("/mgmt/datastores/versions/%s/parameters/%s" %
                         (version, key))

    def modify(self, version, name, restart_required, data_type,
               max_size=None, min_size=None):
        """Mgmt call to modify an existing configuration parameter."""
        body = {
            "configuration-parameter": {
                "name": name,
                "restart_required": int(restart_required),
                "data_type": data_type,
            }
        }
        if max_size is not None:
            body["configuration-parameter"]["max_size"] = max_size
        if min_size is not None:
            body["configuration-parameter"]["min_size"] = min_size
        output = {
            'version': version,
            'parameter_name': name
        }
        url = ("/mgmt/datastores/versions/%(version)s/"
               "parameters/%(parameter_name)s" % output)
        resp, body = self.api.client.put(url, body=body)
        common.check_for_exceptions(resp, body, url)

    def delete(self, version, name):
        """Mgmt call to delete a configuration parameter."""
        output = {
            'version_id': version,
            'parameter_name': name
        }
        url = ("/mgmt/datastores/versions/%(version_id)s/"
               "parameters/%(parameter_name)s" % output)
        resp, body = self.api.client.delete(url)
        common.check_for_exceptions(resp, body, url)


@utils.arg('--datastore', metavar='<datastore>',
           default=None,
           help='ID or name of the datastore to list configuration '
                'parameters for. Optional if the ID of the'
                ' datastore_version is provided.')
@utils.arg('datastore_version',
           metavar='<datastore_version>',
           help='Datastore version name or ID assigned to the '
                'configuration group.')
@utils.arg('parameter', metavar='<parameter>',
           help='Name of the configuration parameter.')
def do_configuration_parameter_show(cs, args):
    """Shows details of a configuration parameter."""
    if args.datastore:
        param = cs.configuration_parameters.get_parameter(
            args.datastore,
            args.datastore_version,
            args.parameter)
    elif utils.is_uuid_like(args.datastore_version):
        param = cs.configuration_parameters.get_parameter_by_version(
            args.datastore_version,
            args.parameter)
    utils.print_object(param)


@utils.arg('--datastore', metavar='<datastore>',
           default=None,
           help='ID or name of the datastore to list configuration '
                'parameters for. Optional if the ID of the'
                ' datastore_version is provided.')
@utils.arg('datastore_version',
           metavar='<datastore_version>',
           help='Datastore version name or ID assigned to the '
                'configuration group.')
def do_configuration_parameter_list(cs, args):
    """Lists available parameters for a configuration group."""
    if args.datastore:
        params = cs.configuration_parameters.parameters(
            args.datastore,
            args.datastore_version)
    elif utils.is_uuid_like(args.datastore_version):
        params = cs.configuration_parameters.parameters_by_version(
            args.datastore_version)
    else:
        raise exceptions.NoUniqueMatch('The datastore name or id is required'
                                       ' to retrieve the parameters for the'
                                       ' configuration group by name.')
    utils.print_list(params, ['name', 'type', 'min_size', 'max_size',
                              'restart_required'])


@utils.arg('datastore_version',
           metavar='<datastore_version>',
           help='Datastore version name or UUID assigned to the '
                'configuration group.')
@utils.arg('name', metavar='<name>',
           help='Name of the datastore configuration parameter.')
@utils.arg('restart_required', metavar='<restart_required>',
           help='Flags the instance to require a restart if this '
                'configuration parameter is new or changed.')
@utils.arg('data_type', metavar='<data_type>',
           help='Data type of the datastore configuration parameter.')
@utils.arg('--max_size', metavar='<max_size>',
           help='Maximum size of the datastore configuration parameter.')
@utils.arg('--min_size', metavar='<min_size>',
           help='Minimum size of the datastore configuration parameter.')
def do_configuration_parameter_create(cs, args):
    """Create datastore configuration parameter"""
    cs.configuration_parameters.create(
        args.datastore_version,
        args.name,
        args.restart_required,
        args.data_type,
        args.max_size,
        args.min_size,
    )


@utils.arg('datastore_version',
           metavar='<datastore_version>',
           help='Datastore version name or UUID assigned to the '
                'configuration group.')
@utils.arg('name', metavar='<name>',
           help='Name of the datastore configuration parameter.')
@utils.arg('restart_required', metavar='<restart_required>',
           help='Sets the datastore configuration parameter if it '
                'requires a restart or not.')
@utils.arg('data_type', metavar='<data_type>',
           help='Data type of the datastore configuration parameter.')
@utils.arg('--max_size', metavar='<max_size>',
           help='Maximum size of the datastore configuration parameter.')
@utils.arg('--min_size', metavar='<min_size>',
           help='Minimum size of the datastore configuration parameter.')
def do_configuration_parameter_modify(cs, args):
    """Modify datastore configuration parameter"""
    cs.configuration_parameters.modify(
        args.datastore_version,
        args.name,
        args.restart_required,
        args.data_type,
        args.max_size,
        args.min_size,
    )


@utils.arg('datastore_version',
           metavar='<datastore_version>',
           help='Datastore version name or UUID assigned to the '
                'configuration group.')
@utils.arg('name', metavar='<name>',
           help='UUID of the datastore configuration parameter.')
def do_configuration_parameter_delete(cs, args):
    """Modify datastore configuration parameter"""
    cs.configuration_parameters.delete(
        args.datastore_version,
        args.name,
    )
