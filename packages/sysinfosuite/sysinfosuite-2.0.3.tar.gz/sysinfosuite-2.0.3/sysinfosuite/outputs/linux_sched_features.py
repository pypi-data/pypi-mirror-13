# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_sched_features(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets scheduler information from target device"
        self.author = "Peter Mikus"
        self.cmd = "cat /sys/kernel/debug/sched_features"
        self.version = "1.0.0"
        self.section = 3
        self.significance = 2
        self.output = ""
        self.status = ""
