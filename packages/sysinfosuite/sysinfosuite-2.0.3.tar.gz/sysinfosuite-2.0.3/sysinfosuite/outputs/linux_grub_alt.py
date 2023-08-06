# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_grub_alt(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets grub configuration"
        self.author = "Peter Mikus"
        self.cmd = "sudo cat /boot/grub/grub.conf"
        self.version = "1.0.0"
        self.section = 3
        self.significance = 3
        self.output = ""
        self.status = ""
