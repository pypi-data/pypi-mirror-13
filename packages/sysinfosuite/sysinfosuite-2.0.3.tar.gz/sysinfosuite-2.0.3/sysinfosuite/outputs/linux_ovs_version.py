# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_ovs_version(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets the version of OpenVSwitch running"
        self.author = "Peter Mikus"
        self.cmd = "ovs-vsctl --version"
        self.version = "1.0.0"
        self.section = 6
        self.significance = 1
        self.output = ""
        self.status = ""
