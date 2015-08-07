__author__ = 'akeshavan'
import nipype.pipeline.engine as pe
import nipype.interfaces.io as nio
import nipype.interfaces.utility as niu
import nipype.interfaces.fsl as fsl
import nipype.interfaces.freesurfer as fs
import os
from glob import glob

subject_list = [s.split("/")[-1][3:8] for s in sorted(glob("/data/henry7/keshavan/munich/data/f2_??_??.nii.gz"))]
print "list of subjects is", subject_list

working = "/data/henry_temp/keshavan/munich"
sink = "/data/henry7/keshavan/munich/analyses"
subjects_dir="/data/henry7/keshavan/munich/analyses/surfaces"
data_dir = "/data/henry7/keshavan/munich/data"

#Run recon all on the lesion filled T1 images
wf = pe.Workflow(name="first")
wf.base_dir = working

inputspec = pe.Node(niu.IdentityInterface(fields=["subject_id"]), name="inputspec")

inputspec.iterables = ("subject_id", subject_list)

#take orig, mask by aparc+aseg (save as nii) then pop over to first.

datagrabber = pe.Node(nio.DataGrabber(infields=["subject_id"],
                                      outfields=["aparc", "orig"],
                                      sort_filelist=False),
                      name="datagrabber", run_without_submitting=True)

datagrabber.inputs.base_directory = subjects_dir
datagrabber.inputs.template = "*"
datagrabber.inputs.field_template = dict(aparc="%s/mri/aparc+aseg.mgz",
                                         orig="%s/mri/orig.mgz")
datagrabber.inputs.template_args = dict(aparc=[["subject_id"]],
                                        orig=[["subject_id"]])

wf.connect(inputspec, "subject_id", datagrabber, "subject_id")

masker = pe.Node(fs.ApplyMask(),
                 name="maskT1")

wf.connect(datagrabber, "orig", masker, "in_file")
wf.connect(datagrabber, "aparc", masker, "mask_file")
renamer = lambda x: x.replace("orig.mgz", "orig_masked.nii.gz")
wf.connect(datagrabber, ('orig', renamer), masker, "out_file")

first = pe.Node(fsl.FIRST(brain_extracted=True),
                name="first")
wf.connect(masker, "out_file", first, "in_file")

sinker = pe.Node(nio.DataSink(), name="sinker")
sinker.inputs.base_directory = sink

wf.connect(inputspec, "subject_id", sinker, "container")

subs = lambda x: [("_subject_id_%s"%x, "")]

wf.connect(inputspec, ("subject_id", subs), sinker, "substitutions")

wf.connect(first, "bvars", sinker, "first.bvars")
wf.connect(first, "original_segmentations", sinker, "first.original")
wf.connect(first, "segmentation_file", sinker, "first.@segmentation")
wf.connect(first, "vtk_surfaces", sinker, "first.vtk")

wf.run(plugin="SGE", plugin_args = {"qsub_args": os.environ["PLUGIN_ARGS"]})
