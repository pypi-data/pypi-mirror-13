# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_sysctl(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets actual kernel parameters at runtime"
        self.author = "Peter Mikus"
        self.cmd = "sysctl -a"
        self.version = "1.0.0"
        self.section = 3
        self.significance = 2
        self.output = ""
        self.status = ""
