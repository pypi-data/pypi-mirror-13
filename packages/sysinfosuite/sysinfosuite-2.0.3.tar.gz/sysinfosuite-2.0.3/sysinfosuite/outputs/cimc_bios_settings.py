# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class cimc_bios_settings(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets the UCS bios settings"
        self.author = "Peter Mikus"
        self.cmd = "biosSettings"
        self.version = "1.0.0"
        self.section = 2
        self.significance = 1
        self.output = ""
        self.status = ""

    def run(self):
        self.pce.proc_ucs240(self.cmd, "")
        self.output = self.pce.proc_output()
        self.status = self.pce.proc_stat()

    def parse_to_xml(self):
        try:
            self.output = ET.XML(self.output)
        except Exception:
            pass
