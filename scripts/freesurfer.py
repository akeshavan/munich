__author__ = 'akeshavan'
import nipype.pipeline.engine as pe
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.io as nio
from glob import glob
import os
import nipype.interfaces.utility as niu

subject_list = [s.split("/")[-1][3:8] for s in sorted(glob("/data/henry7/keshavan/munich/data/f2_??_??.nii.gz"))]
print "list of subjects is", subject_list

working = "/data/henry_temp/keshavan/munich"
sink = "/data/henry7/keshavan/munich/analyses"
subjects_dir="/data/henry7/keshavan/munich/analyses/surfaces"
data_dir = "/data/henry7/keshavan/munich/data"

#Run recon all on the lesion filled T1 images
wf = pe.Workflow(name="freesurfer_recon_all")
wf.base_dir = working

inputspec = pe.Node(niu.IdentityInterface(fields=["subject_id"]), name="inputspec")

inputspec.iterables = ("subject_id", subject_list)

datagrabber = pe.Node(nio.DataGrabber(infields=["subject_id"],
                                      outfields=["t1_filled",
                                                 "t2"],
                                      sort_filelist=True),
                      name="datagrabber",
                      run_without_submitting=True)
datagrabber.inputs.template="*"
datagrabber.inputs.base_directory = data_dir
datagrabber.inputs.template_args = dict(t1_filled=[["subject_id"]], t2=[["subject_id"]])
datagrabber.inputs.field_template = dict(t1_filled="t1_%s_filled.nii.gz", t2="f2_%s.nii.gz")

recon = pe.Node(fs.ReconAll(subjects_dir=subjects_dir, directive="all"),
                name="recon_all")
wf.connect(datagrabber, "t1_filled", recon, "T1_files")
wf.connect(datagrabber, "t2", recon, "T2_file")
wf.connect(inputspec, "subject_id", datagrabber, "subject_id")
wf.connect(inputspec,"subject_id", recon,"subject_id")

wf.run(plugin="SGE", plugin_args={"qsub_args": os.environ["PLUGIN_ARGS"]})
