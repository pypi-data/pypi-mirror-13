import getpass
import os
from cdbclient import exceptions


class BaseAuthPlugin(object):
    """Authenticate as a Racker for novaclient."""

    default_bypass_url = None

    def __init__(self):
        self.opts = {}

    @staticmethod
    def add_opts(parser):
        """Populate and return the parser with the options for this plugin.

        If the plugin does not need any options, it should return the same
        parser untouched.
        """
        return parser

    def parse_opts(self, args):
        """Parse the actual auth-system options if any.

        This method is expected to populate the attribute self.opts with a
        dict containing the options and values needed to make authentication.
        If the dict is empty, the client should assume that it needs the same
        options as the 'keystone' auth system (i.e. os_username and
        os_password).

        Returns the self.opts dict.
        """
        return self.opts

    def get_auth_url(self):
        """Default production auth url."""
        return "https://identity-internal.api.rackspacecloud.com/v2.0"

    def authenticate(self, cls, auth_url):
        """Authenticate against the Rackspace internal auth service."""

        # If not using supernova don't require password on the command line
        # you can set OS_PASSWORD=password to get around the shell command
        # requiring that you pass something.
        if not cls.password or cls.password == 'password':
            cls.password = getpass.getpass()

        body = {
            "auth": {
                "RAX-AUTH:domain": {
                    "name": "Rackspace"
                },
                "passwordCredentials": {
                    "username": cls.user,
                    "password": cls.password,
                }
            }
        }

        if not auth_url.endswith('tokens'):
            auth_url = os.path.join(auth_url, 'tokens')

        # Make sure we follow redirects when trying to reach Keystone
        resp, respbody = cls.request(
            auth_url,
            "POST",
            body=body,
            allow_redirects=True)

        if resp.status_code == 200 or resp.status_code == 201:
            try:
                cls.auth_token = respbody['access']['token']['id']
                cls.tenant_id = respbody['access']['user']['id']
            except KeyError:
                raise exceptions.AuthorizationFailure()

            # Override the bypass_url for cinder/nova in cinder set
            # the management_url as there is no bypass_url functionality
            # set the default url to be localhost.
            default = self.default_bypass_url % cls.tenant_id
            bypass_url = os.environ.get('OS_BYPASS_URL', default)
            if hasattr(cls, 'bypass_url'):
                if not cls.bypass_url:
                    cls.bypass_url = bypass_url
            else:
                cls.management_url = bypass_url

        elif resp.status_code == 305:
            return resp.headers['location']
        else:
            raise exceptions.from_response(resp, body, auth_url)


class NovaAuthPlugin(BaseAuthPlugin):

    default_bypass_url = 'http://localhost:8774/v2/%s'


class CinderAuthPlugin(BaseAuthPlugin):

    default_bypass_url = 'http://localhost:8776/v1/%s'
