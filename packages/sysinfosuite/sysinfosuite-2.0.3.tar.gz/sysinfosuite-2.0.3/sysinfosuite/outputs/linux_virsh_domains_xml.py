# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_virsh_domains_xml(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Show the status of modules in the Linux Kernel"
        self.author = "Peter Mikus"
        self.cmd = "virsh dumpxml"
        self.cmd1 = "virsh list | grep -E -v \"Id.*Name.*State\" | grep \"^ \" | awk '{print $2}'"
        self.version = "1.0.0"
        self.section = 5
        self.significance = 1
        self.output = ""
        self.status = ""

    def run(self):
        self.pce.proc_exec(self.cmd1, "")
        self.output = self.pce.proc_output()
        self.status = self.pce.proc_stat()
        root = ET.Element("virsh_domains")
        if not self.status:
            for domain in self.output.split():
                self.pce.proc_exec(self.cmd+" "+domain, "")
                try:
                    root.insert(0, ET.XML(self.pce.proc_output()))
                except:
                    pass
        self.output = root
