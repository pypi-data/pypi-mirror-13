#!/usr/bin/env python
"""Script for comparing captured information"""

# Modules
import sys
import os
import logging
import subprocess
import tempfile
try:
    import lxml.etree
except ImportError:
    sys.stderr.write('LXML library is required to run the script.\n' \
                     'To install the library run the following command:\n' \
                     '\tUbuntu/Debian: apt-get install python-lxml\n' \
                     '\tFedora/RHEL/CentOS: yum install python-lxml\n')
    sys.exit(2)
try:
    import argparse
except ImportError:
    sys.stderr.write('Argparse library is required to run the script.\n' \
                     'To install the library run the following command:\n' \
                     '\tUbuntu/Debian: apt-get install python-argparse\n' \
                     '\tFedora/RHEL/CentOS: yum install python-argparse\n')
    sys.exit(2)

# Script information
__author__ = "Peter Mikus"
__license__ = "GPLv3"
__version__ = "1.1.0"
__maintainer__ = "Peter Mikus"
__email__ = "pmikus@cisco.com"
__status__ = "Production"

# Logging settings
G_LOGGER = logging.getLogger(__name__)
G_LOGGER.setLevel(logging.DEBUG)
G_LOG_HANDLER = logging.FileHandler("sys_info.log", "w")
G_LOG_FORMAT = logging.Formatter("%(asctime)s: %(name)-12s \
                                 %(levelname)s - %(message)s")
G_LOG_HANDLER.setFormatter(G_LOG_FORMAT)
G_LOGGER.addHandler(G_LOG_HANDLER)

# Color settings
G_COL_GREY = '\033[1;30m'
G_COL_RED = '\033[1;31m'
G_COL_GREEN = '\033[1;32m'
G_COL_YELLOW = '\033[1;33m'
G_COL_BLUE = '\033[1;34m'
G_COL_MAGENTA = '\033[1;35m'
G_COL_CYAN = '\033[1;36m'
G_COL_WHITE = '\033[1;37m'
G_COL_CRIMSON = '\033[1;38m'
G_COL_RESET = '\033[1;m'


class Printer(object):
    """Handles all outputs to stderr, stdout, stdin and file."""
    def __init__(self, file_name=''):
        if file_name:
            sys.stdout = file_name
            sys.stderr = sys.__stderr__
        else:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__


class DiffXml(object):
    """Handles comparision of two files."""
    cmd = ""

    def __init__(self, first, second):
        self.first = lxml.etree.parse(first).getroot()
        self.second = lxml.etree.parse(second).getroot()

    @classmethod
    def sdiff_exec(cls, cmd):
        """Executes the diff"""
        try:
            G_LOGGER.info('Running sdiff (subprocess open): %s', cmd)
            proc_open = subprocess.Popen(cmd,
                                         shell=True,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         close_fds=False)
            child_stdout, _ = proc_open.communicate()
            return child_stdout
        except OSError as ex_error:
            sys.stderr.write('Subprocess open exception: '+str(ex_error)+'\n')
            G_LOGGER.critical('Subprocess open exception: %s', ex_error)
            sys.exit(2)

    def listing(self):
        """Process the diff"""
        try:
            selection = self.first.xpath("//section/function")
            for elem1 in selection:
                sys.stdout.write("Function: "\
                                 +G_COL_GREEN\
                                 +elem1.attrib['id']\
                                 +G_COL_RESET\
                                 +" (Significance: "\
                                 +elem1.attrib['significance']\
                                 +')\n')
        except lxml.etree.XPathSyntaxError as ex_error:
            sys.stderr.write('XPath syntax error: '+str(ex_error)+'\n')
            G_LOGGER.error('XPath syntax error: %s', ex_error)
        except lxml.etree.XPathEvalError as ex_error:
            sys.stderr.write('XPath eval error: '+str(ex_error)+'\n')
            G_LOGGER.error('XPath evaluation error: %s', ex_error)

    def process(self, arg):
        """Process the diff"""
        try:
            if arg.section:
                sel_first = self.first.xpath("//section[contains(@id, \
                                             '"+arg.section+"')]")
                sel_second = self.second.xpath("//section[contains(@id \
                                               , '"+arg.section+"')]")
            elif arg.function:
                sel_first = self.first.xpath("//section/function[contains \
                                             (@id, '"+arg.function+"')]")
                sel_second = self.second.xpath("//section/function[contains \
                                               (@id, '"+arg.function+"')]")
            elif arg.significance:
                sel_first = self.first.xpath("//section/function[contains \
                                     (@significance, '"+arg.significance+"')]")
                sel_second = self.second.xpath("//section/function[contains \
                                     (@significance, '"+arg.significance+"')]")
            elif arg.xpath:
                sel_first = self.first.xpath(arg.xpath)
                sel_second = self.second.xpath(arg.xpath)
            else:
                sel_first = self.first.xpath("//section/function")
                sel_second = self.second.xpath("//section/function")

            for elem1 in sel_first:
                fd1, temp_path1 = tempfile.mkstemp(text=True)
                file1 = os.fdopen(fd1, 'w+t')
                fd2, temp_path2 = tempfile.mkstemp(text=True)
                file2 = os.fdopen(fd2, 'w+t')
                file1.write(lxml.etree.tostring(elem1))
                file1.read()
                for elem2 in sel_second:
                    if elem1.attrib['id'] == elem2.attrib['id']:
                        file2.write(lxml.etree.tostring(elem2))
                file2.read()
                if arg.changes:
                    self.cmd = "sdiff -s -t -w "+arg.width\
                               +" "+temp_path1+" "+temp_path2
                else:
                    self.cmd = "sdiff -t -w "+arg.width\
                               +" "+temp_path1+" "+temp_path2
                sys.stdout.write(self.sdiff_exec(self.cmd)+'\n')
                os.remove(temp_path1)
                os.remove(temp_path2)
        except lxml.etree.XPathSyntaxError as ex_error:
            sys.stderr.write('XPath syntax error: '+str(ex_error)+'\n')
            G_LOGGER.error('XPath syntaxt error: %s', ex_error)
        except lxml.etree.XPathEvalError as ex_error:
            sys.stderr.write('XPath eval error: '+str(ex_error)+'\n')
            G_LOGGER.error('XPath evaluation error: %s', ex_error)


def get_args():
    """Handles command line arguments."""
    parser = argparse.ArgumentParser(description='Script for comparing \
                                     captured information')
    parser.add_argument('--first',
                        metavar='FILE1',
                        type=argparse.FileType('r'),
                        help='First file to compare',
                        required=True)
    parser.add_argument('--second',
                        metavar='FILE2',
                        type=argparse.FileType('r'),
                        help='Second file to compare',
                        required=True)
    parser.add_argument('--section',
                        action='store',
                        help='Display specific section',
                        default='')
    parser.add_argument('--function',
                        action='store',
                        help='Display specific function',
                        default='')
    parser.add_argument('--xpath',
                        action='store',
                        help='XPath expression filter',
                        default='')
    parser.add_argument('--significance',
                        action='store',
                        help='Display specific function',
                        default='')
    parser.add_argument('--listing',
                        action='store_true',
                        help='Display available functions')
    parser.add_argument('--width',
                        action='store',
                        help='Set the width of the columns',
                        default='230')
    parser.add_argument('--changes',
                        action='store_true',
                        help='Display only changes')
    parser.add_argument('--output',
                        metavar='FILE',
                        type=argparse.FileType('wt'),
                        help='Redirect the output to a file')
    parser.add_argument('--version', action='version',
                        version='Script version: '+__version__)
    try:
        return parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))


def main():
    """Main function"""
    arg = get_args()
    Printer(arg.output)
    diff = DiffXml(arg.first, arg.second)

    if arg.listing:
        diff.listing()
    else:
        diff.process(arg)

if __name__ == "__main__":
    main()

