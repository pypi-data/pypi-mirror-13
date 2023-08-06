    # vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2015 Rackspace
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
#
# The source to this project is a fork of the python-troveclient project from
# late 2014, which was written for OpenStack by multiple companies including
# including Rackspace and licensed under the Apache License.

VERSION = "1.0.4"

import os
import pkg_resources
import setuptools
from setuptools.command import easy_install
from setuptools.command.install import install
from setuptools.command.install_scripts import install_scripts
from textwrap import dedent


with open('requirements.txt') as txt:
    requirements = [x.strip() for x in txt.read().splitlines() if x.strip()
                    and not x.startswith('#')]


_script_text = """# Auto generated from 'console_scripts'

import sys

from %(module_name)s import %(import_target)s


if __name__ == "__main__":
    sys.exit(%(invoke_target)s())
"""


def get_script_args(dist, executable):
    """Override entrypoints console_script."""
    header = easy_install.get_script_header("", executable, False)
    for name, ep in dist.get_entry_map('console_scripts').items():
        script_text = _script_text % dict(
            module_name=ep.module_name,
            import_target=ep.attrs[0],
            invoke_target='.'.join(ep.attrs),
        )
        yield (name, header + script_text)


class custom_install_scripts(install_scripts):
    """Intercepts console scripts entry_points and fixes them"""
    command_name = 'install_scripts'

    def run(self):
        import distutils.command.install_scripts

        self.run_command("egg_info")
        self.outfiles = []

        ei_cmd = self.get_finalized_command("egg_info")
        dist = pkg_resources.Distribution(
            ei_cmd.egg_base,
            pkg_resources.PathMetadata(ei_cmd.egg_base, ei_cmd.egg_info),
            ei_cmd.egg_name, ei_cmd.egg_version,
        )
        bs_cmd = self.get_finalized_command('build_scripts')
        executable = getattr(
            bs_cmd, 'executable', easy_install.sys_executable)
        for args in get_script_args(dist, executable):
            self.write_script(*args)


class custom_install(install):
    """This is needed to trigger custom_install_scripts"""
    def run(self):
        install.run(self)


setuptools.setup(
    cmdclass={
        'install': custom_install,
        'install_scripts': custom_install_scripts,
    },
    name="cdbclient",
    version=VERSION,
    author="Rackspace",
    description="Rich client bindings for the Rackspace Cloud Database REST "
                "API.",
    long_description=dedent("""
        Rich client bindings for the Rackspace's Cloud Database service REST
        API. This is a fork of the the python-troveclient project from late
        2014, which was written for OpenStack by multiple companies
        including Rackspace and licensed under the Apache License. It includes
        code to take advantage of new functionality created by Rackspace
        since that time.
    """),
    license="Apache License, Version 2.0",
    url="http://www.rackspace.com/cloud/databases",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
    entry_points={
        "console_scripts": [
            "cdb-cli = cdbclient.shell:main",
            "cdb-setup = cdbclient.cdb_cmd:main_setup",
        ],
        "cdbclient.extension": [
            "backups = cdbclient.v1.backups",
            "configuration_parameters = cdbclient.v1.config_parameters",
            "configurations = cdbclient.v1.configurations",
            "databases = cdbclient.v1.databases",
            "datastore_versions = cdbclient.v1.datastore_versions",
            "datastores = cdbclient.v1.datastores",
            "flavors = cdbclient.v1.flavors",
            "ha = cdbclient.v1.ha",
            "instances = cdbclient.v1.instances",
            "limits = cdbclient.v1.limits",
            "root = cdbclient.v1.root",
            "users = cdbclient.v1.users",
            "versions = cdbclient.v1.versions",
            "schedules = cdbclient.v1.schedules",
        ]
    }
)
