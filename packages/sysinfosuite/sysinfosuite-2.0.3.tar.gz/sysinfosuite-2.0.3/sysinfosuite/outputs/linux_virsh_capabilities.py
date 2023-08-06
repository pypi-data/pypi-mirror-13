# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_virsh_capabilities(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets the KVM capabilities"
        self.author = "Peter Mikus"
        self.cmd = "virsh capabilities"
        self.version = "1.0.0"
        self.section = 4
        self.significance = 1
        self.output = ""
        self.status = ""

    def parse_to_xml(self):
        try:
            self.output = ET.XML(self.output)
        except Exception:
            pass
