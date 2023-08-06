"""
This exists as a super low friction way to use the CDB clients.
"""
from __future__ import print_function
import os
import sys
import getpass
try:
    import ConfigParser
except:
    import configparser as ConfigParser
from supernova import credentials
from supernova import config

try:
    from supernova import executable
except ImportError:
    # supernova requires the novaclient installed
    cwd = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cwd)
    from supernova import executable

TEMPLATE = """
[cdb-dfw]
OS_EXECUTABLE = cdb-cli
OS_USERNAME = '{username}'
OS_PASSWORD = USE_KEYRING['cdbapikey']
OS_TENANT_NAME = '{tenant_id}'
OS_AUTH_SYSTEM = rackspace
OS_REGION_NAME = DFW

[cdb-iad]
OS_EXECUTABLE = cdb-cli
OS_USERNAME = '{username}'
OS_PASSWORD = USE_KEYRING['cdbapikey']
OS_TENANT_NAME = '{tenant_id}'
OS_AUTH_SYSTEM = rackspace
OS_REGION_NAME = DFW

[cdb-lon]
OS_EXECUTABLE = cdb-cli
OS_USERNAME = '{username}'
OS_PASSWORD = USE_KEYRING['cdbapikey']
OS_TENANT_NAME = '{tenant_id}'
OS_AUTH_SYSTEM = rackspace
OS_REGION_NAME = LON

[cdb-ord]
OS_EXECUTABLE = cdb-cli
OS_USERNAME = '{username}'
OS_PASSWORD = USE_KEYRING['cdbapikey']
OS_TENANT_NAME = '{tenant_id}'
OS_AUTH_SYSTEM = rackspace
OS_REGION_NAME = ORD
"""


SUCCESS = """Success?

Now try to hit the API using a call such as:

supernova cdb-iad flavor-list

If this fails, double check that your username, tenant and password are
correct, then delete the file .supernova and run this program again.

If you have other requirements, consider editting the file .supernova directly.
This file can also be moved to your home directory.

For more info on managing the file and auth stuff, please read the
SuperNova docs since that's what this is stealing.

Protip: advanced users can use supernova directly- just set the OS_EXECUTABLE
to the "cdb-cli" CLI tool)
"""

APPEND = """
Your password was stored in the keyring as "cdbapikey", but the .supernova
configuration file was not written because we already found one. If you'd
like to use this exisiting config file with cdbclient, simple append
the following text:
"""

APPEND_2 = """
Then try hittingthe API using a call such as:

supernova cdb-iad flavor-list

If this fails, double check that your username, tenant and password are
correct, then run this program again to update your password credentials
and see if the config needs to change. Or if you won't miss it, delete the
.supernova file and run this program again.
"""

ADDITIONAL= """
If you have other requirements, consider editting the file .supernova directly.
This file can also be moved to your home directory.

For more info on managing the file and auth stuff, please read the
SuperNova docs since that's what this is stealing.

Protip: advanced users can use supernova directly- just set the OS_EXECUTABLE
to the "cdb-cli" CLI tool)
"""

def main_setup(template=TEMPLATE):
    username = raw_input("Please enter your username: ")
    tenant = raw_input("Please enter your tenant: ")
    keyring_name = "global:cdbapikey"
    print("Now enter your apikey. It will be stored in your keyring "
          "under %s:" % keyring_name)
    password = getpass.getpass('apikey: ')

    credentials.password_set(keyring_name, password)

    config_text = template.format(username=username, tenant_id=tenant)

    if not os.path.exists(".supernova"):
        print('Creating the file ".supernova."')
        with open(".supernova", 'w') as f:
            f.write(config_text)

        print(SUCCESS)
        print(ADDITIONAL)
    else:
        print(APPEND)
        print(config_text)
        print(APPEND_2)

    return 0

if __name__ == "__main__":
    main()

