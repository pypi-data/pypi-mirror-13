# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_vpp_conf(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets Cisco VPE configuration"
        self.cmd = "cat /opt/cisco/vpe/etc/qn.conf"
        self.version = "1.0.0"
        self.section = 6
        self.significance = 1
        self.output = ""
        self.status = ""
