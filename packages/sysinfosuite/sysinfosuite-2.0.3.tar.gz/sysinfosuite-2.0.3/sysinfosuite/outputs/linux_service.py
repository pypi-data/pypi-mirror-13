# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_service(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets services status"
        self.author = "Peter Mikus"
        self.cmd = "service --status-all"
        self.version = "1.0.0"
        self.section = 3
        self.significance = 3
        self.output = ""
        self.status = ""
