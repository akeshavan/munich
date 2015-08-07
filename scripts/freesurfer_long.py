__author__ = 'akeshavan'

scanners = ["GE","Si","Ph"]
from glob import glob
import os

"""
for sc in scanners:
    tps = [x.split("/")[-1] for x in sorted(glob("../surfaces/??_%s"%sc))]
    cmd1 = "recon-all -base %s " % (sc) + " -tp ".join(tps)

#I ran this manually

"recon-all -base GE -tp 01_GE -tp 02_GE -tp 03_GE -tp 04_GE -tp 05_GE -tp 06_GE -all"
"recon-all -base Si -tp 01_Si -tp 02_Si -tp 03_Si -tp 04_Si -tp 06_Si -all"
"""

subject_list = [s.split("/")[-1] for s in sorted(glob("/data/henry7/keshavan/munich/analyses/??_??"))]
print "list of subjects is", subject_list

for s in subject_list:
    cmd = "recon-all -long %s %s -all -sd /data/henry7/keshavan/munich/analyses/surfaces" % (s, s.split("_")[-1])
    with open("freesurfer_long_qsub/%s.sh"%s,"w") as f:
        f.write(cmd)
    os.system("qsub %s -N s%s freesurfer_long_qsub/%s.sh"%(os.environ["PLUGIN_ARGS"],s,s))
    print cmd
