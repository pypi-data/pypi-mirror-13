# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class cimc_equipment_fan_module(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets the UCS fan module information"
        self.author = "Peter Mikus"
        self.cmd = "equipmentFanModule"
        self.version = "1.0.0"
        self.section = 1
        self.significance = 2
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
