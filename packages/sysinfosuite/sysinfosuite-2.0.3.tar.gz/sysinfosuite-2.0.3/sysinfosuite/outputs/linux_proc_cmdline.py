# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_proc_cmdline(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets CMD line options"
        self.author = "Peter Mikus"
        self.cmd = "cat /proc/cmdline"
        self.version = "1.0.0"
        self.section = 3
        self.significance = 1
        self.output = ""
        self.status = ""
