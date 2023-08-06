# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_proc_mounts(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets mounted FS information from target device"
        self.author = "Peter Mikus"
        self.cmd = "cat /proc/mounts"
        self.version = "1.0.0"
        self.section = 3
        self.significance = 1
        self.output = ""
        self.status = ""
