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

"""
Command-line interface to the Rackspace Cloud Databases API.
"""

from __future__ import print_function

import argparse
import getpass
import logging
import os
import sys

import pkg_resources
import six

import cdbclient
from cdbclient import client
import cdbclient.extension
from cdbclient.openstack.common.apiclient import exceptions as exc
from cdbclient.openstack.common import strutils
from cdbclient import utils


DEFAULT_OS_DATABASE_API_VERSION = "1.0"
DEFAULT_TROVE_ENDPOINT_TYPE = 'publicURL'
DEFAULT_TROVE_SERVICE_TYPE = 'rax:database'

logger = logging.getLogger(__name__)


class TroveClientArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(TroveClientArgumentParser, self).__init__(*args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)
        # FIXME(lzyeval): if changes occur in argparse.ArgParser._check_value
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        self.exit(2, "error: %(errmsg)s\nTry '%(mainp)s help %(subp)s'"
                     " for more information.\n" %
                     {'errmsg': message.split(choose_from)[0],
                      'mainp': progparts[0],
                      'subp': progparts[2]})


class OpenStackTroveShell(object):

    def get_base_parser(self):
        parser = TroveClientArgumentParser(
            prog='cdb-cli',
            description=__doc__.strip(),
            epilog='See "cdb-cli help COMMAND" '
                   'for help on a specific command.',
            add_help=False,
            formatter_class=OpenStackHelpFormatter,
        )

        # Global arguments
        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS)

        parser.add_argument('--version',
                            action='version',
                            version=cdbclient.__version__,
                            help="Show cdbclient version.")

        parser.add_argument('--debug',
                            action='store_true',
                            default=utils.env('TROVECLIENT_DEBUG',
                                              default=False),
                            help="Print debugging output.")

        parser.add_argument('--insecure',
                            action='store_true',
                            default=utils.env('TROVECLIENT_INSECURE',
                                              default=False),
                            help="Don't validate SSL Certs")

        parser.add_argument('--json',
                            action='store_true',
                            default=utils.env('OS_JSON_OUTPUT',
                                              default=False),
                            help='Output JSON instead of prettyprint. '
                                 'Defaults to env[OS_JSON_OUTPUT].')

        parser.add_argument('--bypass-url',
                            metavar='<bypass-url>',
                            default=utils.env('TROVE_BYPASS_URL'),
                            help='Defaults to env[TROVE_BYPASS_URL].')
        parser.add_argument('--bypass_url',
                            help=argparse.SUPPRESS)

        parser.add_argument('--retries',
                            metavar='<retries>',
                            type=int,
                            default=0,
                            help='Number of retries.')

        parser.add_argument('--os-auth-system',
                            metavar='<auth-system>',
                            default=utils.env('OS_AUTH_SYSTEM'),
                            help='Defaults to env[OS_AUTH_SYSTEM].')
        parser.add_argument('--os_auth_system',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-username',
                            metavar='<auth-username>',
                            default=utils.env('OS_USERNAME',
                                              'TROVE_USERNAME'),
                            help='Username to authenticate with '
                                 'Defaults to env[OS_USERNAME].')
        parser.add_argument('--os_username',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-password',
                            metavar='<auth-password>',
                            default=utils.env('OS_PASSWORD',
                                              'TROVE_PASSWORD'),
                            help='Password to authenticate with '
                                 'Defaults to env[OS_PASSWORD].')
        parser.add_argument('--os_password',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-tenant-id', '--os-tenant-name',
                            metavar='<tenant-id>',
                            default=utils.env('OS_TENANT_ID',
                                              'OS_TENANT_NAME'),
                            help='Tenant to request authorization on. '
                                 'Defaults to env[OS_TENANT_ID].')
        parser.add_argument('--os_tenant_id',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-auth-token',
                            default=utils.env('OS_AUTH_TOKEN'),
                            help='Defaults to env[OS_AUTH_TOKEN]')

        parser.add_argument('--os-auth-url',
                            default=utils.env('OS_AUTH_URL'),
                            help='Defaults to env[OS_AUTH_URL]')

        parser.add_argument('--os-cacert',
                            default=utils.env('OS_CACERT'),
                            help='Specify ca cert to use.'
                                 'Defaults to env[OS_CACERT]')

        parser.add_argument('--os-region-name',
                            metavar='<region-name>',
                            default=utils.env('OS_REGION_NAME'),
                            help='Specify the region to use. '
                                 'Defaults to env[OS_REGION_NAME].')
        parser.add_argument('--os_region_name',
                            help=argparse.SUPPRESS)

        parser.add_argument('--endpoint-type',
                            metavar='<endpoint-type>',
                            default=utils.env(
                                'TROVE_ENDPOINT_TYPE',
                                default=DEFAULT_TROVE_ENDPOINT_TYPE),
                            help='Defaults to env[TROVE_ENDPOINT_TYPE] or '
                            + DEFAULT_TROVE_ENDPOINT_TYPE + '.')
        parser.add_argument('--endpoint_type',
                            help=argparse.SUPPRESS)

        parser.add_argument('--service-type',
                            metavar='<service-type>',
                            default=utils.env('OS_SERVICE_TYPE',
                                              'TROVE_SERVICE_TYPE'),
                            help='Defaults to database for most actions.')
        parser.add_argument('--service_type',
                            help=argparse.SUPPRESS)

        parser.add_argument('--service-name',
                            metavar='<service-name>',
                            default=utils.env('TROVE_SERVICE_NAME'),
                            help='Defaults to env[TROVE_SERVICE_NAME].')
        parser.add_argument('--service_name',
                            help=argparse.SUPPRESS)

        return parser

    def get_subcommand_parser(self):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        self._find_commands(subparsers)
        self._find_actions(subparsers, self)

        self.extensions.sort()

        for extension in self.extensions:
            self._find_actions(subparsers, extension.module)

        self._add_bash_completion_subparser(subparsers)

        return parser

    def _add_bash_completion_subparser(self, subparsers):
        subparser = subparsers.add_parser(
            'bash_completion',
            add_help=False,
            formatter_class=OpenStackHelpFormatter)

        self.subcommands['bash_completion'] = subparser
        subparser.set_defaults(func=self.do_bash_completion)

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hyphen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(
                command,
                help=help,
                description=desc,
                add_help=False,
                formatter_class=OpenStackHelpFormatter)

            subparser.add_argument('-h', '--help',
                                   action='help',
                                   help=argparse.SUPPRESS,)

            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def _find_commands(self, subparsers):
        for attr, callback in utils.get_commands():
            # I prefer to be hyphen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(
                command,
                help=help,
                description=desc,
                add_help=False,
                formatter_class=OpenStackHelpFormatter)

            subparser.add_argument('-h', '--help',
                                   action='help',
                                   help=argparse.SUPPRESS,)

            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def setup_debugging(self, debug):
        if not debug:
            return

        streamformat = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
        logging.basicConfig(level=logging.DEBUG,
                            format=streamformat)

    def main(self, argv):
        # Parse args once to find version and debug settings
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self.setup_debugging(options.debug)
        self.options = options

        # build available subcommands based on version
        self.extensions = client.Client.discover_extensions()
        self._run_extension_hooks('__pre_parse_args__')

        subcommand_parser = self.get_subcommand_parser()
        self.parser = subcommand_parser

        if options.help or not argv:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)
        self._run_extension_hooks('__post_parse_args__', args)

        # Short-circuit and deal with help right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

        os_username = args.os_username
        os_password = args.os_password
        os_auth_url = args.os_auth_url
        os_region_name = args.os_region_name
        os_tenant_id = args.os_tenant_id
        os_auth_system = args.os_auth_system
        endpoint_type = args.endpoint_type
        insecure = args.insecure
        service_type = args.service_type
        service_name = args.service_name
        cacert = args.os_cacert
        bypass_url = args.bypass_url
        auth_plugin = None

        if not endpoint_type:
            endpoint_type = DEFAULT_TROVE_ENDPOINT_TYPE

        if not service_type:
            service_type = DEFAULT_TROVE_SERVICE_TYPE
            service_type = utils.get_service_type(args.func) or service_type

        # FIXME(usrleon): Here should be restrict for project id same as
        # for os_username or os_password but for compatibility it is not.

        if not utils.isunauthenticated(args.func):

            if not os_username:
                os_username = raw_input('Username: ')

            if not os_tenant_id:
                os_tenant_id = raw_input('Tenant ID: ')

            if not os_password:
                os_password = getpass.getpass()

            if not os_auth_url:
                os_auth_url = self.get_auth_url(os_region_name, os_auth_system)

            set_bypass = (os_auth_system == 'racker' or
                          os_region_name in ['STAGING', 'DEV', 'QA'])

            if not bypass_url and set_bypass:
                bypass_url = self.get_bypass_url(os_region_name,
                                                 os_auth_system,
                                                 os_tenant_id)

        if not os_auth_url:
            raise exc.CommandError("You must provide an auth url "
                                   "via either --os-auth-url or "
                                   "env[OS_AUTH_URL] or specify an "
                                   "auth_system which defines a default "
                                   "url with --os-auth-system or "
                                   "env[OS_AUTH_SYSTEM]")

        self.cs = client.Client(os_username,
                                os_password, os_tenant_id, os_auth_url,
                                insecure, region_name=os_region_name,
                                tenant_id=os_tenant_id,
                                endpoint_type=endpoint_type,
                                extensions=self.extensions,
                                service_type=service_type,
                                service_name=service_name,
                                retries=options.retries,
                                http_log_debug=args.debug,
                                cacert=cacert,
                                bypass_url=bypass_url,
                                auth_system=os_auth_system)

        try:
            if not utils.isunauthenticated(args.func):
                self.cs.authenticate()
        except exc.Unauthorized:
            raise exc.CommandError("Invalid Credentials.")
        except exc.AuthorizationFailure:
            raise exc.CommandError("Unable to authorize user")

        # Override printing to json output
        if args.json:
            utils.json_output = True
        else:
            utils.json_output = False

        args.func(self.cs, args)

    def get_auth_url(self, region_name, auth_system):
        """Sets the default auth urls for this region."""

        region = region_name.lower()
        internal_auth = 'identity-internal.api.rackspacecloud.com'
        public_auth = 'identity.api.rackspacecloud.com'

        if auth_system == 'racker':
            # Default to the internal url for Racker Auth
            auth = internal_auth
        else:
            auth = public_auth

        if region in ['ord', 'dfw', 'iad', 'hkg']:
            return 'https://%s/v2.0' % auth
        elif region == 'lon':
            return 'https://lon.%s/v2.0' % auth
        elif region == 'syd':
            return 'https://vip.syd.%s/v2.0' % auth
        else:
            return 'https://staging.%s/v2.0' % internal_auth

    def get_bypass_url(self, region_name, auth_system, tenant_id):
        """Sets the default bypass_url for this region."""
        region = region_name.lower()
        clouddb = 'databases.api.rackspacecloud.com'
        prefix = 'admin.'
        if region in ['staging', 'dev', 'qa']:
            if auth_system == 'racker':
                prefix = 'mgmt.'
            else:
                prefix = ''
            clouddb = 'clouddb.rackspace.net'
            region = '%s.ord1' % region
        return 'https://%s%s.%s/v1.0/%s' % (
            prefix, region, clouddb, tenant_id
        )

    def _run_extension_hooks(self, hook_type, *args, **kwargs):
        """Run hooks for all registered extensions."""
        for extension in self.extensions:
            extension.run_hooks(hook_type, *args, **kwargs)

    def do_bash_completion(self, args):
        """Prints arguments for bash_completion.

        Prints all of the commands and options to stdout so that the
        trove.bash_completion script doesn't have to hard code them.
        """
        commands = set()
        options = set()
        for sc_str, sc in list(self.subcommands.items()):
            commands.add(sc_str)
            for option in list(sc._optionals._option_string_actions.keys()):
                options.add(option)

        commands.remove('bash-completion')
        commands.remove('bash_completion')
        print(' '.join(commands | options))

    @utils.arg('command', metavar='<subcommand>', nargs='?',
               help='Display help for <subcommand>.')
    def do_help(self, args):
        """Displays help about this program or one of its subcommands."""
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            self.parser.print_help()


# I'm picky about my shell help.
class OpenStackHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog, indent_increment=2, max_help_position=43,
                 width=None):
        super(OpenStackHelpFormatter, self).__init__(prog, indent_increment,
                                                     max_help_position, width)

    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(OpenStackHelpFormatter, self).start_section(heading)

    def _format_usage(self, usage, actions, groups, prefix):
        """Formats the argument list to correct argument positions.

        Print positionals before optionals in the usage string to help
        users avoid argparse nargs='*' problems.

        ex: 'trove create --databases <db_name> <name> <flavor_id>'
        fails with 'error: too few arguments', but this succeeds:
        'trove create <name> <flavor_id> --databases <db_name>'
        """
        if prefix is None:
            prefix = 'usage: '

        # if usage is specified, use that
        if usage is not None:
            usage = usage % dict(prog=self._prog)

        # if no optionals or positionals are available, usage is just prog
        elif usage is None and not actions:
            usage = '%(prog)s' % dict(prog=self._prog)

        # if optionals and positionals are available, calculate usage
        elif usage is None:
            prog = '%(prog)s' % dict(prog=self._prog)

            # split optionals from positionals
            optionals = []
            positionals = []
            for action in actions:
                if action.option_strings:
                    optionals.append(action)
                else:
                    positionals.append(action)

            # build full usage string
            format = self._format_actions_usage
            action_usage = format(optionals + positionals, groups)
            usage = ' '.join([s for s in [prog, action_usage] if s])

            # wrap the usage parts if it's too long
            text_width = self._width - self._current_indent
            if len(prefix) + len(usage) > text_width:

                # break usage into wrappable parts
                part_regexp = r'\(.*?\)+|\[.*?\]+|\S+'
                opt_usage = format(optionals, groups)
                pos_usage = format(positionals, groups)
                opt_parts = argparse._re.findall(part_regexp, opt_usage)
                pos_parts = argparse._re.findall(part_regexp, pos_usage)
                assert ' '.join(opt_parts) == opt_usage
                assert ' '.join(pos_parts) == pos_usage

                # helper for wrapping lines
                def get_lines(parts, indent, prefix=None):
                    lines = []
                    line = []
                    if prefix is not None:
                        line_len = len(prefix) - 1
                    else:
                        line_len = len(indent) - 1
                    for part in parts:
                        if line_len + 1 + len(part) > text_width:
                            lines.append(indent + ' '.join(line))
                            line = []
                            line_len = len(indent) - 1
                        line.append(part)
                        line_len += len(part) + 1
                    if line:
                        lines.append(indent + ' '.join(line))
                    if prefix is not None:
                        lines[0] = lines[0][len(indent):]
                    return lines

                # if prog is short, follow it with optionals or positionals
                if len(prefix) + len(prog) <= 0.75 * text_width:
                    indent = ' ' * (len(prefix) + len(prog) + 1)
                    if pos_parts:
                        if prog == 'trove':
                            # "trove help" called without any subcommand
                            lines = get_lines([prog] + opt_parts, indent,
                                              prefix)
                            lines.extend(get_lines(pos_parts, indent))
                        else:
                            lines = get_lines([prog] + pos_parts, indent,
                                              prefix)
                            lines.extend(get_lines(opt_parts, indent))
                    elif opt_parts:
                        lines = get_lines([prog] + opt_parts, indent, prefix)
                    else:
                        lines = [prog]

                # if prog is long, put it on its own line
                else:
                    indent = ' ' * len(prefix)
                    parts = pos_parts + opt_parts
                    lines = get_lines(parts, indent)
                    if len(lines) > 1:
                        lines = []
                        lines.extend(get_lines(pos_parts, indent))
                        lines.extend(get_lines(opt_parts, indent))
                    lines = [prog] + lines

                # join lines into usage
                usage = '\n'.join(lines)

        # prefix with 'usage:'
        return '%s%s\n\n' % (prefix, usage)


def main():
    try:
        if sys.version_info >= (3, 0):
            OpenStackTroveShell().main(sys.argv[1:])
        else:
            OpenStackTroveShell().main(map(strutils.safe_decode,
                                           sys.argv[1:]))
    except KeyboardInterrupt:
        print("... terminating trove client", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.debug(e, exc_info=1)
        message = six.text_type(e)
        if not isinstance(message, six.string_types):
            message = str(message)
        print("ERROR: %s" % strutils.safe_encode(message), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
