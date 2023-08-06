# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_proc_cpuinfo(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Handles CPU info output"
        self.author = "Peter Mikus"
        self.cmd = "cat /proc/cpuinfo"
        self.version = "1.0.0"
        self.section = 2
        self.significance = 1
        self.output = ""
        self.status = ""
