# Modules
import xml.etree.cElementTree as ET
import sysinfosuite.collect

class linux_cgroup_cpuset(sysinfosuite.collect.OutputsBase):
    def __init__(self, pc):
        self.pce = pc
        self.description = "Gets cgroup CPU information from target device"
        self.author = "Peter Mikus"
        self.cmd = "for a in $(find /sys/fs/cgroup/cpuset -type d) ; do echo $a ; echo -n \"CPUs = \" ; cat $a/cpuset.cpus ; echo -n \"MEMs = \" ; cat $a/cpuset.mems ; echo -n \"PIDs/TIDs = \" ; cat $a/tasks | tr '\\012' ',' ; echo ; echo ; done"
        self.version = "1.0.0"
        self.section = 2
        self.significance = 2
        self.output = ""
        self.status = ""
