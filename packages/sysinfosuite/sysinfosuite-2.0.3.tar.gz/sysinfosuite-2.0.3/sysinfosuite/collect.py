#!/usr/bin/env python
"""Script to gather information from local or remote system"""

# Modules
import datetime as DT
import hashlib
import json
import logging
import os
import pkgutil
import socket
import subprocess
import sys
import xml.etree.ElementTree as ET
from operator import itemgetter
from itertools import groupby
try:
    import argparse
except ImportError:
    sys.stderr.write('Argparse library is required to run the script.\n' \
                     'To install the library run the following command:\n' \
                     '\tUbuntu/Debian: apt-get install python-argparse\n' \
                     '\tFedora/RHEL/CentOS: yum install python-argparse\n')
    sys.exit(2)
try:
    import paramiko
except ImportError:
    sys.stderr.write('Paramiko library is required to run the script.\n' \
                     'To install the library run the following command:\n' \
                     '\tUbuntu/Debian: apt-get install python-paramiko\n' \
                     '\tFedora/RHEL/CentOS: yum install python-paramiko\n')
    sys.exit(2)

# Script information
__author__ = "Peter Mikus"
__license__ = "GPLv3"
__version__ = "2.0.3"
__maintainer__ = "Peter Mikus"
__email__ = "pmikus@cisco.com"
__status__ = "Production"


# Global variables
# Logging settings
G_LOGGER = logging.getLogger(__name__)
G_LOGGER.setLevel(logging.DEBUG)
G_LOG_HANDLER = logging.FileHandler("sys-info-suite.log", "w")
G_LOG_FORMAT = logging.Formatter("%(asctime)s: %(name)-12s \
                                 %(levelname)s - %(message)s")
G_LOG_HANDLER.setFormatter(G_LOG_FORMAT)
G_LOGGER.addHandler(G_LOG_HANDLER)


# VNET SLA output suite
G_SUITE = ["linux_cpupower_frequency_info",
           "linux_cpupower_idle_info",
           "linux_ethtool",
           "linux_lscpu",
           "linux_lspci",
           "linux_meminfo",
           "linux_proc_cpuinfo",
           "linux_proc_meminfo",
           "linux_bridges_status",
           "linux_centos_release",
           "linux_grub",
           "linux_cgroup_cpuset",
           "linux_grub_alt",
           "linux_installed_packages_dpkg",
           "linux_installed_packages_yum",
           "linux_kernel_version",
           "linux_links_status",
           "linux_linux_version",
           "linux_lsblk",
           "linux_lsmod",
           "linux_os_release",
           "linux_proc_cmdline",
           "linux_proc_mounts",
           "linux_ps",
           "linux_rhel_release",
           "linux_service",
           "linux_sysctl",
           "linux_sched_features",
           "linux_dtime",
           "linux_virsh_capabilities",
           "linux_virsh_domains",
           "linux_virsh_domains_xml",
           "linux_ovs_bridges_status",
           "linux_ovs_version",
           "linux_vpp_conf"]

# CIMC inventory output
G_SUITE_UCS_FULL = ["cimc_compute_rack_unit"]
G_SUITE_UCS = ["cimc_network_adapter_unit",
               "cimc_equipment_psu",
               "cimc_equipment_fan_module",
               "cimc_compute_board",
               "cimc_mgmt_controller",
               "cimc_bios_unit",
               "cimc_pci_equip_slot"]

G_STACK_SECTION = {1: "Physical Infrastructure",
                   2: "Compute Hardware",
                   3: "Compute Operating System",
                   4: "Compute Virtualization Infrastructure / Hypervisor",
                   5: "Compute Virtualization Functions / VMs",
                   6: "Network Virtualization Infastructure / vSwitch"}


class Configuration(object):
    """Handles parsing and saving configuration file"""
    def __init__(self, config):
        self.config = config

    def load_config(self, jfile):
        """Load configuration from file"""
        try:
            self.config = json.load(open(jfile, 'r'))
        except IOError as ex_error:
            sys.stderr.write('Cannot open configuration file: ' \
                             +str(ex_error)+'\n')
            G_LOGGER.critical('Cannot open configuration file: %s', ex_error)
            sys.exit(2)
        except ValueError as ex_error:
            sys.stderr.write('Cannot load configuration: ' \
                             +str(ex_error)+'\n')
            G_LOGGER.critical('Cannot load configuration: %s', ex_error)
            sys.exit(2)
        except TypeError as ex_error:
            sys.stderr.write('Cannot load configuration: ' \
                             +str(ex_error)+'\n')
            G_LOGGER.critical('Cannot load configuration: %s', ex_error)
            sys.exit(2)
        return self.config

    def save_config(self, config, jfile):
        """Save configuration to file"""
        self.config = config
        try:
            json.dump(self.config, open(jfile, 'w'))
        except IOError as ex_error:
            sys.stderr.write('Cannot write configuration file: ' \
                             +str(ex_error)+'\n')
            G_LOGGER.critical('Cannot write configuration file: %s', ex_error)
            sys.exit(2)


class Printer(object):
    """Handles all outputs to stderr, stdout, stdin and file"""
    sha256_hash = 'N/A'

    def __init__(self, file_name=''):
        if file_name:
            sys.stdout = open(file_name, 'w')
            sys.stderr = sys.__stderr__
        else:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    def print_hash(self):
        """Print hash of output"""
        sys.stderr.write(self.sha256_hash+'\n')

    @classmethod
    def print_list(cls, suite):
        """Print check outputs"""
        for key, section in groupby(sorted(suite.suite_all,
                                           key=itemgetter(1, 2)),
                                    lambda x: x[1]):
            sys.stdout.write(G_STACK_SECTION[key]+'\n')
            for i in section:
                sys.stdout.write('\t\033[1;32m'+i[0]+'\033[1;m '+i[4]+'\n')
                sys.stdout.write('\t\t'+i[3]+'\n')
                sys.stdout.write('\t\t'+i[5]+'\n\n')

    @classmethod
    def print_check(cls, suite):
        """Print check outputs"""
        for key in sorted(suite.suite_all, key=itemgetter(1, 2)):
            if key[6] == 0:
                sys.stdout.write('[\033[1;32m OK \033[1;m]\t'+key[0]+'\n')
            else:
                sys.stdout.write('[\033[1;31m ERR \033[1;m]\t'+key[0]+'\n')
                sys.stdout.write('\tCommand: '+str(key[5])+'\n')
                sys.stdout.write('\t'+str(key[7])+'\n')

    def print_suite(self, suite):
        """Print all outputs into xml"""
        root = ET.Element("stack")
        root.attrib["script_version"] = __version__
        if not suite.suite_host:
            root.attrib["host"] = "localhost"
        else:
            root.attrib["host"] = suite.suite_host

        for key, sec in groupby(sorted(suite.suite_all, key=itemgetter(1, 2)),
                                lambda x: x[1]):
            section = ET.Element("section")
            section.attrib["id"] = str(key)
            section.attrib["name"] = G_STACK_SECTION[key]
            for i in sec:
                output = ET.Element("function")
                output.attrib["id"] = i[0]
                output.attrib["significance"] = str(i[2])
                output.attrib["time"] = i[8]
                output.attrib["version"] = i[4]

                exec_cmd = ET.Element("exec_command")
                exec_cmd.text = "<![CDATA["+str(i[5]).decode('utf-8')+"]]>"
                output.append(exec_cmd)

                exec_code = ET.Element("exec_return_code")
                exec_code.text = str(i[6]).decode('utf-8')
                output.append(exec_code)

                if ET.iselement(i[7]):
                    exec_output = ET.Element("exec_output")
                    exec_output.insert(0, i[7])
                    output.append(exec_output)
                else:
                    exec_output = ET.Element("exec_output")
                    exec_output.text = "<![CDATA[\n"\
                                        +str(i[7]).decode('utf-8')+"]]>"
                    output.append(exec_output)
                section.append(output)
            root.append(section)
        self.print_indent(root)
        sys.stdout.write(ET.tostring(root))
        self.sha256_hash = hashlib.sha256(ET.tostring(root)).hexdigest()

    def print_indent(self, elem, level=0):
        """Handles pretty print for XML"""
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.print_indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


class ProcessCall(object):
    """Handles sub-processes/SSH/HTTP calls"""
    # pylint: disable=R0902
    def __init__(self, host, username, password, keyfile):
        self.child_stdout = ''
        self.child_stat = 0
        self.child_stderr = ''
        self.ssh = ''
        self.host = host
        self.username = username
        self.password = password
        self.keyfile = keyfile

    def proc_output(self):
        """Returns output from stdout or stderr"""
        if not self.child_stat:
            return self.child_stdout
        else:
            return self.child_stderr

    def proc_stat(self):
        """Returns status of the command call"""
        return self.child_stat

    def proc_local(self, cmd, cmd_input):
        """Create subprocess and run the command"""
        try:
            G_LOGGER.info('Running command on local host (subprocess)')
            G_LOGGER.info('Command to run: %s', cmd)
            proc_open = subprocess.Popen(cmd,
                                         shell=True,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         close_fds=True)
            self.child_stdout, self.child_stderr = proc_open.communicate(\
                        cmd_input)
            self.child_stat = proc_open.wait()
        except OSError as ex_error:
            self.child_stat = 255
            G_LOGGER.critical('Subprocess open exception: %s', ex_error)

    # pylint: disable=R0913
    def proc_remote(self, cmd, host, username, password, keyfile):
        """Create SSH session and run the command"""
        try:
            G_LOGGER.info('Creating SSH session to host: %s', host)
            if not self.ssh:
                self.ssh = paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(\
                        paramiko.AutoAddPolicy())
                self.ssh.connect(host, username=username, password=password,
                                 key_filename=keyfile)
            G_LOGGER.info('Command to run over SSH: %s', cmd)
            tmp_stdin, tmp_stdout, tmp_stderr = self.ssh.exec_command(cmd)
            tmp_stdin.close()
            self.child_stdout = tmp_stdout.read()
            self.child_stderr = tmp_stderr.read()
            self.child_stat = tmp_stdout.channel.recv_exit_status()
        except paramiko.AuthenticationException as ex_error:
            self.ssh.close()
            self.ssh = ''
            self.child_stat = 255
            sys.stderr.write('SSH: '+str(ex_error)+'\n')
            G_LOGGER.critical('SSH to device %s: %s', self.host, ex_error)
        except socket.error as ex_error:
            self.ssh.close()
            self.ssh = ''
            self.child_stat = 255
            sys.stderr.write('SSH: '+str(ex_error)+'\n')
            G_LOGGER.critical('SSH to device %s: %s', self.host, ex_error)

    def proc_exec(self, cmd, cmd_input):
        """Execute command locally or over SSH session"""
        if not self.host:
            self.proc_local(cmd, cmd_input)
        else:
            self.proc_remote(cmd, self.host, self.username,
                             self.password, self.keyfile)

    def proc_ucs240(self, cmd, cmd_input):
        """Create subprocess and run the command"""
        try:
            G_LOGGER.info('Running command on local host (subprocess)')
            cmd1 = "curl -k -X POST --data '<aaaLogin \
                    inName=\""+self.username+"\" \
                    inPassword=\""+self.password+"\" />' \
                    https://"+self.host+"/nuova"
            G_LOGGER.info('Command to run: %s', cmd1)
            proc_open = subprocess.Popen(cmd1,
                                         shell=True,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         close_fds=True)
            self.child_stdout, self.child_stderr = proc_open.communicate(\
                        cmd_input)
            self.child_stat = proc_open.wait()

            if not self.child_stat:
                ccc = ET.fromstring(self.child_stdout).attrib.get('outCookie')
                if ccc:
                    G_LOGGER.info('Connected to CIMC host: %s, [Cookie: %s]',
                                  self.host, ccc)
                    cmd2 = "curl -k -X POST --data '<configResolveClass \
                            cookie=\""+ccc+"\" \
                            inHierarchical=\"true\" \
                            classId=\""+cmd+"\" />' \
                            https://"+self.host+"/nuova"
                    G_LOGGER.info('Command to run: %s', cmd2)
                    proc_o = subprocess.Popen(cmd2,
                                              shell=True,
                                              stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              close_fds=True)
                    self.child_stdout, self.child_stderr = proc_o.communicate(\
                                cmd_input)
                    self.child_stat = proc_o.wait()
                    cmd3 = "curl -k -X POST --data '<aaaLogout \
                            inCookie=\""+ccc+"\" />' \
                            https://"+self.host+"/nuova"
                    G_LOGGER.info('Loging out from CIMC of host: %s, [Cookie: \
                                  %s]', self.host, ccc)
                    proc_open = subprocess.Popen(cmd3,
                                                 shell=True,
                                                 stdin=subprocess.PIPE,
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE,
                                                 close_fds=True)
                else:
                    G_LOGGER.critical('Failed to get cookie from CIMC')
            else:
                G_LOGGER.critical('Failed to get data from CIMC: %s',
                                  self.child_stderr)
        except OSError as ex_error:
            self.child_stat = 255
            G_LOGGER.critical('Subprocess open exception: %s', ex_error)


class OutputsBase(object):
    """Parent class for modules implements the behavior"""
    description = ""
    cmd = ""
    version = ""
    section = 0
    significance = 0
    output = ""
    status = ""

    def __init__(self, pc):
        self.pce = pc

    def run(self):
        """Runs the execution of funtion and returns output and stat"""
        self.pce.proc_exec(self.cmd, "")
        self.status = self.pce.proc_stat()
        self.output = self.pce.proc_output()

    def get_command(self):
        """Return command to run"""
        return self.cmd

    def get_version(self):
        """Return version"""
        return self.version

    def get_status(self):
        """Return status"""
        return self.status

    def get_description(self):
        """Return description of command"""
        return self.description

    def get_section(self):
        """Return section of stack"""
        return self.section

    def get_significance(self):
        """Return significance of function"""
        return self.significance

    def get_output(self):
        """Return output of command. Try to parse to xml"""
        if not self.status:
            self.parse_to_xml()
        return self.output

    def parse_to_xml(self):
        """Parse output to XML"""
        pass


class OutputSuite(object):
    """Handles calling outputs in iteration by dynamically loading modules"""
    suite_all = ()

    def __init__(self, host, username, password, keyfile):
        self.suite_host = host
        self.pce = ProcessCall(host, username, password, keyfile)

    def list_modules(self):
        """List the package modules"""
        path = os.path.join(os.path.dirname(__file__), "outputs")
        modules = pkgutil.iter_modules(path=[path])
        for _, mod_name, _ in modules:
            if mod_name not in sys.modules:
                try:
                    loaded_mod = __import__("sysinfosuite.outputs."+mod_name,
                                            fromlist=[mod_name])
                    loaded_class = getattr(loaded_mod, mod_name)(self.pce)
                    self.suite_all += ((mod_name,
                                        loaded_class.get_section(),
                                        loaded_class.get_significance(),
                                        loaded_class.get_description(),
                                        loaded_class.get_version(),
                                        loaded_class.get_command(),
                                        loaded_class.get_status(),
                                        loaded_class.get_output(),
                                        str(DT.datetime.utcnow())+" UTC"),)
                # pylint: disable=W0703
                except Exception:
                    G_LOGGER.error('Error execution of output function "%s"',
                                   mod_name)

    def run_module(self, modules):
        """Run the suite by calling modules from package"""
        for mod_name in modules:
            if mod_name not in sys.modules:
                try:
                    loaded_mod = __import__("sysinfosuite.outputs."+mod_name,
                                            fromlist=[mod_name])
                    loaded_class = getattr(loaded_mod, mod_name)(self.pce)
                    loaded_class.run()
                    self.suite_all += ((mod_name,
                                        loaded_class.get_section(),
                                        loaded_class.get_significance(),
                                        loaded_class.get_description(),
                                        loaded_class.get_version(),
                                        loaded_class.get_command(),
                                        loaded_class.get_status(),
                                        loaded_class.get_output(),
                                        str(DT.datetime.utcnow())+" UTC"),)
                    G_LOGGER.debug('Return code: %s',
                                   loaded_class.get_status())
                # pylint: disable=W0703
                except Exception:
                    G_LOGGER.error('Error execution of output function "%s"',
                                   mod_name)

    def run_all_linux_modules(self):
        """Run all linux modules from package"""
        path = os.path.join(os.path.dirname(__file__), "outputs")
        modules = pkgutil.iter_modules(path=[path])
        for _, mod_name, _ in modules:
            if mod_name not in sys.modules and mod_name.startswith("linux"):
                try:
                    loaded_mod = __import__("sysinfosuite.outputs."+mod_name,
                                            fromlist=[mod_name])
                    loaded_class = getattr(loaded_mod, mod_name)(self.pce)
                    loaded_class.run()
                    self.suite_all += ((mod_name,
                                        loaded_class.get_section(),
                                        loaded_class.get_significance(),
                                        loaded_class.get_description(),
                                        loaded_class.get_version(),
                                        loaded_class.get_command(),
                                        loaded_class.get_status(),
                                        loaded_class.get_output(),
                                        str(DT.datetime.utcnow())+" UTC"),)
                    G_LOGGER.debug('Return code: %s', loaded_class.get_status())
                    # pylint: disable=W0703
                except Exception:
                    G_LOGGER.error('Error execution of output function "%s"',
                                   mod_name)

    def run_all_cimc_modules(self):
        """Run all cimc modules from package"""
        path = os.path.join(os.path.dirname(__file__), "outputs")
        modules = pkgutil.iter_modules(path=[path])
        for _, mod_name, _ in modules:
            if mod_name not in sys.modules and mod_name.startswith("cimc"):
                try:
                    loaded_mod = __import__("sysinfosuite.outputs."+mod_name,
                                            fromlist=[mod_name])
                    loaded_class = getattr(loaded_mod, mod_name)(self.pce)
                    loaded_class.run()
                    self.suite_all += ((mod_name,
                                        loaded_class.get_section(),
                                        loaded_class.get_significance(),
                                        loaded_class.get_description(),
                                        loaded_class.get_version(),
                                        loaded_class.get_command(),
                                        loaded_class.get_status(),
                                        loaded_class.get_output(),
                                        str(DT.datetime.utcnow())+" UTC"),)
                    G_LOGGER.debug('Return code: %s', loaded_class.get_status())
                    # pylint: disable=W0703
                except Exception:
                    G_LOGGER.error('Error execution of output function "%s"',
                                   mod_name)

    def run_all_modules(self):
        """Run all modules from package"""
        path = os.path.join(os.path.dirname(__file__), "outputs")
        modules = pkgutil.iter_modules(path=[path])
        for _, mod_name, _ in modules:
            if mod_name not in sys.modules:
                try:
                    loaded_mod = __import__("sysinfosuite.outputs."+mod_name,
                                            fromlist=[mod_name])
                    loaded_class = getattr(loaded_mod, mod_name)(self.pce)
                    loaded_class.run()
                    self.suite_all += ((mod_name,
                                        loaded_class.get_section(),
                                        loaded_class.get_significance(),
                                        loaded_class.get_description(),
                                        loaded_class.get_version(),
                                        loaded_class.get_command(),
                                        loaded_class.get_status(),
                                        loaded_class.get_output(),
                                        str(DT.datetime.utcnow())+" UTC"),)
                    G_LOGGER.debug('Return code: %s', loaded_class.get_status())
                    # pylint: disable=W0703
                except Exception:
                    G_LOGGER.error('Error execution of output function "%s"',
                                   mod_name)

def get_args():
    """Command line arguments handling"""
    parser = argparse.ArgumentParser(description='Script for gathering \
                                     the running configuration from host')
    device = parser.add_argument_group('Authentication for device')
    device.add_argument('--device', action='store',
                        help='HOST device to get the information from',
                        default='')
    device.add_argument('--cimc', action='store',
                        help='CIMC device to get the BIOS information',
                        default='')
    device.add_argument('--user', action='store', default='')
    device.add_argument('--password', action='store', default='')
    parser.add_argument('--check', action='store_true',
                        help='check if functions are supported',
                        default=False)
    parser.add_argument('--interactive', action='store_true',
                        help='run script in interactive mode',
                        default=False)
    parser.add_argument('--listing', action='store_true',
                        help='list abvailable functions',
                        default=False)
    parser.add_argument('--hashing', action='store_true',
                        help='print hash of output',
                        default=False)
    parser.add_argument('--output', action='store', metavar='FILE',
                        help='redirect the output to a file')
    parser.add_argument('--keyfile', action='store', metavar='FILE',
                        help='specify SSH key file for authentication')
    parser.add_argument('--json', action='store',
                        help='json configuration file',
                        default='')
    parser.add_argument('--version', action='version',
                        version='Script version: '+__version__)
    try:
        return parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))


def run_interactive():
    """Interactive mode handling"""
    config = ''
    device = raw_input("Enter the host [leave blank for localhost]: ")
    if device:
        keyfile = raw_input("Enter the keyfile [leave blank if N/A]: ")
        user = raw_input("Enter the username for host: ")
        password = raw_input("Enter the password: ")
    else:
        user = ''
        password = ''
        keyfile = ''
    sys.stdout.write('Please select type of device:\n')
    sys.stdout.write('1. Cisco CIMC BIOS\n')
    sys.stdout.write('2. Linux host\n')
    choice = raw_input('Enter your choice [1-2] : ')
    if choice == "1":
        device_type = "cimc"
        suite = G_SUITE_UCS
    else:
        device_type = "linux"
        suite = G_SUITE
    output = raw_input("Enter the output file [leave blank for stdout]: ")
    save = raw_input("Save configuration file? [Yes/No]: ")
    config = {device_type+"_"+device: {'device': device,
                                       'device_type': device_type,
                                       'user': user,
                                       'password': password,
                                       'output': output,
                                       'keyfile': keyfile,
                                       'suite': suite}}
    if save == "Yes" or save == "Y" or save == "y" or save == "yes":
        jfile = raw_input("Enter name of configuration file: ")
        Configuration('').save_config(config, jfile)
    return config


def run_config(arg, config):
    """Run config"""
    for device in config:
        config[device].setdefault('device', '')
        config[device].setdefault('user', '')
        config[device].setdefault('password', '')
        config[device].setdefault('keyfile', '')
        config[device].setdefault('device_type', 'linux')
        config[device].setdefault('suite', '')
        config[device].setdefault('output', '')

        suite = OutputSuite(config[device]['device'],
                            config[device]['user'],
                            config[device]['password'],
                            config[device]['keyfile'])
        printer = Printer(config[device]['output'])

        if arg.check:
            suite.run_module(config[device]['suite'])
            printer.print_check(suite)
        elif arg.listing:
            suite.list_modules()
            printer.print_list(suite)
        else:
            suite.run_module(config[device]['suite'])
            printer.print_suite(suite)
        if arg.hashing:
            printer.print_hash()

def main():
    """Main function"""
    arg = get_args()
    if arg.cimc:
        config = {"cimc_"+arg.cimc: {'device': arg.cimc,
                                     'device_type': "cimc",
                                     'user': arg.user,
                                     'password': arg.password,
                                     'output': arg.output,
                                     'keyfile': arg.keyfile,
                                     'suite': G_SUITE_UCS}}
    else:
        config = {"host_"+arg.device: {'device': arg.device,
                                       'device_type': "linux",
                                       'user': arg.user,
                                       'password': arg.password,
                                       'output': arg.output,
                                       'keyfile': arg.keyfile,
                                       'suite': G_SUITE}}
    if arg.interactive:
        config = run_interactive()
    if arg.json:
        config = Configuration('').load_config(arg.json)
    run_config(arg, config)


if __name__ == "__main__":
    main()
