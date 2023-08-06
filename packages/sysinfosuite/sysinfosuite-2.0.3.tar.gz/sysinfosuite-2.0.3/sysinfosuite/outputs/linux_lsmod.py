# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_lsmod(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Show the status of modules in the Linux Kernel"
        self.author = "Peter Mikus"
        self.cmd = "lsmod | sort"
        self.version = "1.0.0"
        self.section = 3
        self.significance = 2
        self.output = ""
        self.status = ""
