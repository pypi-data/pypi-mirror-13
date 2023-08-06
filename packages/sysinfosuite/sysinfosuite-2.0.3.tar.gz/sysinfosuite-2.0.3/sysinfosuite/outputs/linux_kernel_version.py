# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_kernel_version(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets various system information"
        self.author = "Peter Mikus"
        self.cmd = "uname -a"
        self.version = "1.0.0"
        self.section = 3
        self.significance = 1
        self.output = ""
        self.status = ""
