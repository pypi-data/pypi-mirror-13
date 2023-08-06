#!/usr/bin/env python2
# Author: echel0n <sickrage.tv@gmail.com>
# URL: http://www.github.com/sickragetv/sickrage/
#
# This file is part of SickRage.
#
# SickRage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickRage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import ctypes
import os
import sys

import urllib3.contrib

def root_check():
    try:
        return not os.getuid() == 0
    except AttributeError:
        return not ctypes.windll.shell32.IsUserAnAdmin() != 0

def install_pip():
    print("Downloading pip ...")
    import urllib2

    url = "https://bootstrap.pypa.io/get-pip.py"
    file_name = os.path.abspath(os.path.join(os.path.dirname(__file__), url.split('/')[-1]))
    u = urllib2.urlopen(url)
    with open(file_name, 'wb') as f:
        meta = u.info()
        block_sz = 8192
        while True:
            buf = u.read(block_sz)
            if not buf:
                break
            f.write(buf)

    print("Installing pip ...")
    import subprocess
    subprocess.call([sys.executable, file_name] + ([], ['--user'])[root_check()])

    print("Cleaning up downloaded pip files")
    os.remove(file_name)


def install_packages(file):
    import pip
    from pip.commands.install import InstallCommand
    from pip.exceptions import InstallationError

    constraints = os.path.abspath(os.path.join(os.path.dirname(__file__), 'constraints.txt'))
    pip_install_cmd = InstallCommand()

    # list installed packages
    try:
        installed = [x.project_name.lower() for x in pip.get_installed_distributions(local_only=True, user_only=root_check())]
    except:
        installed = []

    # read requirements file
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), file))) as f:
        packages = [x.strip() for x in f.readlines() if x.strip().lower() not in installed]

    # install requirements packages
    options = pip_install_cmd.parse_args([])[0]
    options.use_user_site = root_check()
    options.constraints = [constraints]
    options.quiet = 1

    for i, pkg_name in enumerate(packages, start=1):
        try:
            print(r"[%3.2f%%]::Installing %s package" % (i * 100 / len(packages), pkg_name))
            pip_install_cmd.run(options, [pkg_name])
        except InstallationError:
            try:
                options.ignore_dependencies = True
                pip_install_cmd.run(options, [pkg_name])
            except:
                continue
        except IndexError:
            continue

    if len(packages) > 0:
        return True


def upgrade_packages():
    from pip.commands.list import ListCommand
    from pip.commands.install import InstallCommand
    from pip.exceptions import InstallationError

    constraints = os.path.abspath(os.path.join(os.path.dirname(__file__), 'constraints.txt'))
    pip_install_cmd = InstallCommand()
    pip_list_cmd = ListCommand()

    while True:
        # list packages that need upgrading
        try:
            options = pip_list_cmd.parse_args([])[0]
            options.use_user_site = root_check()
            options.cache_dir = None
            options.outdated = True

            packages = [p.project_name for p, y, _ in pip_list_cmd.find_packages_latest_versions(options)
                        if getattr(p, 'version', 0) != getattr(y, 'public', 0)]
        except:
            packages = []

        options = pip_install_cmd.parse_args([])[0]
        options.use_user_site = root_check()
        options.constraints = [constraints]
        options.cache_dir = None
        options.upgrade = True
        options.quiet = 1

        for i, pkg_name in enumerate(packages, start=1):
            try:
                print(r"[%3.2f%%]::Upgrading %s package" % (i * 100 / len(packages), pkg_name.lower()))
                pip_install_cmd.run(options, [pkg_name])
            except InstallationError:
                try:
                    options.ignore_dependencies = True
                    pip_install_cmd.run(options, [pkg_name])
                except:
                    continue
            except IndexError:
                continue
        else:
            break


def install_ssl():
    try:
        print("Installing and Patching SiCKRAGE SSL Contexts")
        import urllib3.contrib.pyopenssl
        urllib3.contrib.pyopenssl.inject_into_urllib3()
        urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST = "MEDIUM"
    except ImportError:
        install_packages("ssl.txt")
        os.execl(sys.executable, sys.executable, *sys.argv)


def install_requirements(optional=False, ssl=False):
    # install ssl packages
    if ssl:
        try:
            install_ssl()
        except:
            pass

    print("Checking for required SiCKRAGE packages, please stand by ...")
    install_packages('requirements.txt')

    if optional:
        print("Checking for optional SiCKRAGE packages, please stand by ...")
        try:
            install_packages('optional.txt')
        except:
            pass

    print("Checking for upgradable SiCKRAGE packages, please stand by ...")
    upgrade_packages()
