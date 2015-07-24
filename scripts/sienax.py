__author__ = 'akeshavan'
from nipype.interfaces.fsl.base import FSLCommand, FSLCommandInputSpec
from nipype.interfaces.base import (TraitedSpec, File, traits,
                                    isdefined)
from glob import glob
import os
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as niu
import nipype.interfaces.io as nio


# nipype interface
class SIENAXInputSpec(FSLCommandInputSpec):
    in_file = File(exists=True, mandatory=True,
                   position=1, copyfile=False,
                  argstr='%s',
                  desc='input data file')
    output_dir = traits.Directory(mandatory=False,
                  argstr='-o %s',
                  desc='output folder', hash_files=False)
    debug = traits.Bool(argstr='-d',
        desc="Use verbose logging.", usedefault=True,position=-1)
    bet_options = traits.String(argstr='-B "%s"',
        desc="BET options")
    use_2class = traits.Bool(False, argstr='-2', usedefault=True,
        desc="Use two-class segmentation (don't segment gray and white matter)")
    is_t2 = traits.Bool(argstr="-t2",
                        desc="T2-weighted input image")
    ignore_t = traits.Float(argstr="-t %f",
                            desc="ignore from t (mm) upwards in MNI/Talairach space")
    ignore_b = traits.Float(argstr="-b %f",
                            desc="ignore from b (mm) downwards in MNI/Talairach space (b should probably be negative)")
    regional = traits.Bool(argstr="-r",
                           desc="regional- use standard-space masks to give peripheral cortex GM volume (3-class segmentation only)")
    lesion_mask = traits.File(argstr="-lm %s",
                              desc = "use lesion (or lesion+CSF) mask to remove incorrectly labelled 'grey matter' voxels ")
    seg_options = traits.String(argstr = '-S "%s"',
                              desc="options to pass to FAST segmentation")

class SIENAXOutputSpec(TraitedSpec):
    html_report = traits.File(exists=True)
    report = traits.File(exists=True)
    nifti_files = traits.List(traits.File())
    images = traits.List(traits.File())
    flirt_outputs = traits.List(traits.File())


class SIENAX(FSLCommand):
    _cmd = 'sienax'
    input_spec = SIENAXInputSpec
    output_spec = SIENAXOutputSpec

    def _format_arg(self, name, spec, value):
        if not isdefined(self.inputs.output_dir):
            self.inputs.output_dir = os.path.abspath(".")
        return super(SIENAX, self)._format_arg(name,spec,value)

    def _list_outputs(self):
        outputs = self.output_spec().get()
        od = self.inputs.output_dir
        print od
        outputs["html_report"] = os.path.join(od,"report.html")
        outputs["report"] = os.path.join(od,"report.sienax")
        outputs["images"] = glob(os.path.join(od,"*.png"))
        outputs["flirt_outputs"] = glob(os.path.join(od,"*.mat"))+[os.path.join(od,"I2std.avscale")]
        outputs["nifti_files"] = glob(os.path.join(od,"*.nii*"))
        print outputs
        return outputs

#workflow
subject_list = [s.split("/")[-1][3:8] for s in sorted(glob("/data/henry7/keshavan/munich/data/f2_??_??.nii.gz"))]
print "list of subjects is", subject_list

working = "/data/henry_temp/keshavan/munich"
sink = "/data/henry7/keshavan/munich/analyses"
subjects_dir="/data/henry7/keshavan/munich/analyses/surfaces"
data_dir = "/data/henry7/keshavan/munich/data"

# Run sienax on T1 and T2 images separately

wf = pe.Workflow(name="sienax")
wf.base_dir = working

inputspec = pe.Node(niu.IdentityInterface(fields=["subject_id"]), name="inputspec")

inputspec.iterables = ("subject_id", subject_list)

datagrabber = pe.Node(nio.DataGrabber(infields=["subject_id"],
                                      outfields=["t1",
                                                 "t2",
                                                 "lesion_mask"],
                                      sort_filelist=True),
                      name="datagrabber",
                      run_without_submitting=True)

datagrabber.inputs.template="*"
datagrabber.inputs.base_directory = data_dir
datagrabber.inputs.template_args = dict(t1=[["subject_id"]],
                                        t2=[["subject_id"]],
                                        lesion_mask=[["subject_id"]])
datagrabber.inputs.field_template = dict(t1="t1_%s.nii.gz",
                                         t2="f2_%s.nii.gz",
                                         lesion_mask="lesion_*_%s.nii.gz")

t1_sx = pe.Node(SIENAX(regional=True),
                name="t1w_sienax")
#t2_sx = pe.Node(SIENAX(regional=True, is_t2=True),
#                name="t2w_sienax")

wf.connect(datagrabber, "t1", t1_sx, "in_file")
wf.connect(datagrabber, "lesion_mask", t1_sx, "lesion_mask")

#wf.connect(datagrabber, "t2", t2_sx, "in_file")
#wf.connect(datagrabber, "lesion_mask", t2_sx, "lesion_mask")

sinker = pe.Node(nio.DataSink(), name="sinker")
sinker.inputs.base_directory = sink

for i, node in enumerate([t1_sx]):#, t2_sx]):
    wf.connect(node, "html_report", sinker, "sienax.t%d.@html" % (i+1))
    wf.connect(node, "report", sinker, "sienax.t%d.@report" % (i+1))
    wf.connect(node, "images", sinker, "sienax.t%d.@images" % (i+1))
    wf.connect(node, "flirt_outputs", sinker, "sienax.t%d.@flirt" % (i+1))

wf.connect(inputspec, "subject_id", sinker, "container")

subs = lambda x: [("_subject_id_%s"%x, "")]

wf.connect(inputspec, ("subject_id", subs), sinker, "substitutions")
wf.connect(inputspec, "subject_id", datagrabber, "subject_id")

wf.run()
