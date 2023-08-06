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

from __future__ import print_function

import errno
import os
import signal
import shutil
import sys
import xml.etree.ElementTree as ET

import daemon
import libvirt
import pyghmi.ipmi.bmc as bmc
from six.moves import configparser

import exception


# Power states
POWEROFF = 0
POWERON = 1

# BMC status
RUNNING = 'running'
DOWN = 'down'

# Boot device maps
GET_BOOT_DEVICES_MAP = {
    'network': 4,
    'hd': 8,
    'cdrom': 0x14,
}

SET_BOOT_DEVICES_MAP = {
    'network': 'network',
    'hd': 'hd',
    'optical': 'cdrom',
}


DEFAULT_SECTION = 'VirtualBMC'
CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.vbmc')


class libvirt_open(object):

    def __init__(self, uri, readonly=False):
        self.uri = uri
        self.readonly = readonly

    def __enter__(self):
        try:
            if self.readonly:
                self.conn = libvirt.openReadOnly(self.uri)
            else:
                self.conn = libvirt.open(self.uri)

            return self.conn

        except libvirt.libvirtError as e:
            raise exception.LibvirtConnectionOpenError(uri=self.uri, error=e)

    def __exit__(self, type, value, traceback):
        self.conn.close()


def get_libvirt_domain(conn, domain):
    try:
        return conn.lookupByName(domain)
    except libvirt.libvirtError:
        raise exception.DomainNotFound(domain=domain)


def check_libvirt_connection_and_domain(uri, domain):
    with libvirt_open(uri, readonly=True) as conn:
        get_libvirt_domain(conn, domain)


def is_pid_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


class VirtualBMC(bmc.Bmc):

    def __init__(self, username, password, port, address,
                 domain_name, libvirt_uri):
        super(VirtualBMC, self).__init__({username: password},
                                         port=port, address=address)
        self.libvirt_uri = libvirt_uri
        self.domain_name = domain_name

    def get_boot_device(self):
        with libvirt_open(self.libvirt_uri, readonly=True) as conn:
            domain = get_libvirt_domain(conn, self.domain_name)
            parsed = ET.fromstring(domain.XMLDesc())
            boot_devs = parsed.findall('.//os/boot')
            boot_dev = boot_devs[0].attrib['dev']
            return GET_BOOT_DEVICES_MAP.get(boot_dev, 0)

    def set_boot_device(self, bootdevice):
        device = SET_BOOT_DEVICES_MAP.get(bootdevice)
        if device is None:
            print('Uknown boot device: %s' % bootdevice)
            return 0xd5

        with libvirt_open(self.libvirt_uri) as conn:
            domain = get_libvirt_domain(conn, self.domain_name)
            parsed = ET.fromstring(domain.XMLDesc())
            os = parsed.find('os')
            boot_list = os.findall('boot')

            # Clear boot list
            for boot_el in boot_list:
                os.remove(boot_el)

            boot_el = ET.SubElement(os, 'boot')
            boot_el.set('dev', device)

            try:
                conn.defineXML(ET.tostring(parsed))
            except libvirt.libvirtError as e:
                print('Failed setting the boot device to "%s" on the '
                      '"%s" domain' % (device, self.domain_name),
                      file=sys.stderr)

    def get_power_state(self):
        try:
            with libvirt_open(self.libvirt_uri, readonly=True) as conn:
                domain = get_libvirt_domain(conn, self.domain_name)
                if domain.isActive():
                    return POWERON
        except libvirt.libvirtError as e:
            print('Error getting the power state of domain "%s". '
                  'Error: %s' % (self.domain_name, e), file=sys.stderr)
            return

        return POWEROFF

    def power_off(self):
        try:
            with libvirt_open(self.libvirt_uri) as conn:
                domain = get_libvirt_domain(conn, self.domain_name)
                domain.destroy()
        except libvirt.libvirtError as e:
            print('Error powering off the domain "%s". Error: %s' %
                  (self.domain_name, e), file=sys.stderr)
            return

    def power_on(self):
        try:
            with libvirt_open(self.libvirt_uri) as conn:
                domain = get_libvirt_domain(conn, self.domain_name)
                domain.create()
        except libvirt.libvirtError as e:
            print('Error powering on the domain "%s". Error: %s' %
                  (self.domain_name, e))
            return


class VirtualBMCManager(object):

    def _parse_config(self, domain_name):
        config_path = os.path.join(CONFIG_PATH, domain_name, 'config')
        if not os.path.exists(config_path):
            raise exception.DomainNotFound(domain=domain_name)

        config = configparser.ConfigParser()
        config.read(config_path)

        bmc = {}
        for item in ('username', 'password', 'address',
                     'domain_name', 'libvirt_uri'):
            bmc[item] = config.get(DEFAULT_SECTION, item)

        # Port needs to be int
        bmc['port'] = int(config.get(DEFAULT_SECTION, 'port'))

        return bmc

    def _show(self, domain_name):
        running = False
        try:
            pidfile_path = os.path.join(CONFIG_PATH, domain_name, 'pid')
            with open(pidfile_path, 'r') as f:
                pid = int(f.read())

            running = is_pid_running(pid)
        except IOError:
            pass

        bmc_config = self._parse_config(domain_name)
        bmc_config['status'] = RUNNING if running else DOWN
        return bmc_config

    def add(self, username, password, port, address,
            domain_name, libvirt_uri):
        # Check libvirt and domain
        check_libvirt_connection_and_domain(libvirt_uri, domain_name)

        domain_path = os.path.join(CONFIG_PATH, domain_name)
        try:
            os.makedirs(domain_path)
        except OSError as e:
            if e.errno == errno.EEXIST:
                sys.exit('Domain %s already exist' % domain_name)

        config_path = os.path.join(domain_path, 'config')
        with open(config_path, 'w') as f:
            config = configparser.ConfigParser()
            config.add_section(DEFAULT_SECTION)
            config.set(DEFAULT_SECTION, 'username', username)
            config.set(DEFAULT_SECTION, 'password', password)
            config.set(DEFAULT_SECTION, 'port', port)
            config.set(DEFAULT_SECTION, 'address', address)
            config.set(DEFAULT_SECTION, 'domain_name', domain_name)
            config.set(DEFAULT_SECTION, 'libvirt_uri', libvirt_uri)
            config.write(f)

    def delete(self, domain_name):
        domain_path = os.path.join(CONFIG_PATH, domain_name)
        if not os.path.exists(domain_path):
            raise exception.DomainNotFound(domain=domain_name)

        self.stop(domain_name)
        shutil.rmtree(domain_path)

    def start(self, domain_name):
        domain_path = os.path.join(CONFIG_PATH, domain_name)
        if not os.path.exists(domain_path):
            raise exception.DomainNotFound(domain=domain_name)

        bmc_config = self._parse_config(domain_name)

        # Check libvirt and domain
        check_libvirt_connection_and_domain(
            bmc_config['libvirt_uri'], domain_name)

        pidfile_path = os.path.join(domain_path, 'pid')

        with daemon.DaemonContext(stderr=sys.stderr):
            # FIXME(lucasagomes): pyghmi start the sockets when the
            # class is instantiated, therefore we need to create the object
            # within the daemon context
            vbmc = VirtualBMC(**bmc_config)

            # Save the PID number
            with open(pidfile_path, 'w') as f:
                f.write(str(os.getpid()))

            vbmc.listen()

    def stop(sel, domain_name):
        domain_path = os.path.join(CONFIG_PATH, domain_name)
        if not os.path.exists(domain_path):
            raise exception.DomainNotFound(domain=domain_name)

        pidfile_path = os.path.join(domain_path, 'pid')
        pid = None
        try:
            with open(pidfile_path, 'r') as f:
                pid = int(f.read())
        except IOError:
            # LOG
            return
        else:
            os.remove(pidfile_path)

        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass

    def list(self):
        bmcs = []
        try:
            for domain in os.listdir(CONFIG_PATH):
                bmcs.append(self._show(domain))
        except OSError as e:
            if e.errno == errno.EEXIST:
                return bmcs

        return bmcs

    def show(self, domain_name):
        return self._show(domain_name)
