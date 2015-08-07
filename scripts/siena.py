___author__ = 'akeshavan'
from nipype.interfaces.fsl.base import FSLCommand, FSLCommandInputSpec
from nipype.interfaces.base import (TraitedSpec, File, traits,
                                    isdefined)
from glob import glob
import os
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as niu
import nipype.interfaces.io as nio
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.fsl as fsl
import shutil

# nipype interface
class SIENAXInputSpec(FSLCommandInputSpec):
    in_file = File(exists=True, mandatory=True,
                   position=1, copyfile=False,
                  argstr='%s',
                  desc='input data file')
    skull_file = File(exists=True, mandatory=True)
    mask_file = File(exists=True, mandatory=True)
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
    _cmd = '/data/henry7/keshavan/munich/scripts/sienax'
    input_spec = SIENAXInputSpec
    output_spec = SIENAXOutputSpec

    def _format_arg(self, name, spec, value):
        if not isdefined(self.inputs.output_dir):
            self.inputs.output_dir = os.path.abspath(".")

        skull_file = os.path.abspath("I_brain_skull.nii.gz")
        mask_file = os.path.abspath("I_brain_mask.nii.gz")
        strip_file = os.path.abspath("I_brain.nii.gz")

        shutil.copyfile(self.inputs.skull_file, skull_file)
        shutil.copyfile(self.inputs.mask_file, mask_file)
        shutil.copyfile(self.inputs.in_file, strip_file)

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

class SIENAInputSpec(SIENAXInputSpec):
    in_file = File(exists=True, mandatory=True,
               position=1, copyfile=False,
              argstr='%s',
              desc='input data file')

    second_file = File(exists=True,
                       mandatory=True,
                       position=2,
                       copyfile=False,
                       argstr="%s",
                       desc="second timepoint")

    skull_file2 = File(exists=True, mandatory=True)
    mask_file2 = File(exists=True, mandatory=True)


class SIENAOutputSpec(TraitedSpec):
    all_files = traits.List(traits.File())

class SIENA(FSLCommand):
    _cmd = "/data/henry7/keshavan/munich/scripts/siena"
    input_spec = SIENAInputSpec
    output_spec = SIENAOutputSpec

    def _format_arg(self, name, trait_spec, value):
        if not isdefined(self.inputs.output_dir):
            self.inputs.output_dir = os.path.abspath(".")

        skull_file = os.path.abspath("A_brain_skull.nii.gz")
        mask_file = os.path.abspath("A_brain_mask.nii.gz")
        strip_file = os.path.abspath("A_brain.nii.gz")

        shutil.copyfile(self.inputs.skull_file, skull_file)
        shutil.copyfile(self.inputs.mask_file, mask_file)
        shutil.copyfile(self.inputs.in_file, strip_file)

        skull_file = os.path.abspath("B_brain_skull.nii.gz")
        mask_file = os.path.abspath("B_brain_mask.nii.gz")
        strip_file = os.path.abspath("B_brain.nii.gz")

        shutil.copyfile(self.inputs.skull_file2, skull_file)
        shutil.copyfile(self.inputs.mask_file2, mask_file)
        shutil.copyfile(self.inputs.second_file, strip_file)

        return super(SIENA, self)._format_arg(name,trait_spec,value)

    def _list_outputs(self):
        outputs = self.output_spec().get()
        od = self.inputs.output_dir
        outputs["all_files"] = glob(os.path.join(od,"*"))
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
                                                 #"t2",
                                                 "mask",
                                                 #"lesion_mask"
                                                 ],
                                      sort_filelist=True),
                      name="datagrabber",
                      run_without_submitting=True)

datagrabber.inputs.template="*"
datagrabber.inputs.base_directory = subjects_dir
datagrabber.inputs.template_args = dict(t1=[["subject_id"]],
                                        #t2=[["subject_id"]],
                                        mask=[["subject_id"]],
                                        #lesion_mask=[["subject_id"]]
                                        )
datagrabber.inputs.field_template = dict(t1="%s/mri/orig.mgz",
                                         mask = "%s/mri/aparc+aseg.mgz",
                                         #t2="f2_%s.nii.gz",
                                         #lesion_mask="lesion_*_%s.nii.gz"
                                          )

reo = pe.Node(fsl.Reorient2Std(),name="reorient")
reo2 = reo.clone("reorient2")
reo3 = reo.clone("reorient3")

convert_to_nii = pe.Node(fs.MRIConvert(out_type="niigz"), name="convert_to_nifti")
convert_to_nii2 = convert_to_nii.clone("convert2")
convert_to_nii3 = convert_to_nii2.clone("convert3")

t1_sx = pe.Node(SIENAX(regional=True, debug=True, bet_options="-f 0"),
                name="t1w_sienax")

bin_brain = pe.Node(fs.Binarize(dilate=1, min=0.5), name="binarize_aparc")

bin_skull = pe.Node(fs.Binarize(invert=True, erode=1, min=0.5), name="binarize_aparc_inv")


mask_t1 = pe.Node(fs.ApplyMask(subjects_dir=subjects_dir),
                  name="apply_mask_t1")

mask_skull = pe.Node(fs.ApplyMask(subjects_dir=subjects_dir),
                  name="apply_t1_mask_skull")

#wf.connect(datagrabber, "t1", mask_t1, "in_file")
#wf.connect(datagrabber, "t1", mask_skull, "in_file")

wf.connect(datagrabber, "mask", bin_brain, "in_file")
wf.connect(datagrabber, "mask", bin_skull, "in_file")

#wf.connect(bin_brain, "binary_file", mask_t1, "mask_file")
#wf.connect(bin_skull, "binary_file", mask_skull, "mask_file")

wf.connect(datagrabber,"t1", convert_to_nii, "in_file")
wf.connect(bin_skull, "binary_file", convert_to_nii2, "in_file")
wf.connect(bin_brain, "binary_file", convert_to_nii3, "in_file")

wf.connect(convert_to_nii, "out_file", reo, "in_file")
wf.connect(convert_to_nii2, "out_file", reo2, "in_file")
wf.connect(convert_to_nii3, "out_file", reo3, "in_file")

wf.connect(reo3, "out_file", mask_t1, "mask_file")
wf.connect(reo, "out_file", mask_t1, "in_file")

wf.connect(reo2, "out_file", mask_skull, "mask_file")
wf.connect(reo, "out_file", mask_skull, "in_file")

wf.connect(mask_t1, "out_file", t1_sx, "in_file")
wf.connect(mask_skull, "out_file", t1_sx, "skull_file")
wf.connect(reo3, "out_file", t1_sx, "mask_file")

sinker = pe.Node(nio.DataSink(), name="sinker")

for i, node in enumerate([t1_sx]):#, t2_sx]):
    wf.connect(node, "html_report", sinker, "sienax.t%d.@html" % (i+1))
    wf.connect(node, "report", sinker, "sienax.t%d.@report" % (i+1))
    wf.connect(node, "images", sinker, "sienax.t%d.@images" % (i+1))
    wf.connect(node, "flirt_outputs", sinker, "sienax.t%d.@flirt" % (i+1))

wf.connect(inputspec, "subject_id", sinker, "container")

subs = lambda x: [("_subject_id_%s"%x, "")]

wf.connect(inputspec, ("subject_id", subs), sinker, "substitutions")
wf.connect(inputspec, "subject_id", datagrabber, "subject_id")

"""

SIENA pair-wise

"""

def pairwise_splitter(subject_id, t1_files, mask_files, skull_files):
    import itertools
    # split subject_id's by scanner type, then pairwise choose
    scanners = ["GE", "Si", "Ph"]

    tp1_files = []
    tp1mask_files = []
    tp1skull_files = []
    tp2_files = []
    tp2mask_files = []
    tp2skull_files = []
    tp1_subs = []
    tp2_subs = []

    for sc in scanners:
        #valid_tps = [s for s in subject_id if s.endswith(sc)]
        t1s = [t1_files[i] for i, s in enumerate(subject_id) if s.endswith(sc)]
        masks = [mask_files[i] for i, s in enumerate(subject_id) if s.endswith(sc)]
        skulls = [skull_files[i] for i, s in enumerate(subject_id) if s.endswith(sc)]

        for idx_tp1, idx_tp2 in itertools.combinations(range(len(t1s)),2):
            tp1_files.append(t1s[idx_tp1])
            tp2_files.append(t1s[idx_tp2])
            tp1skull_files.append(skulls[idx_tp1])
            tp1mask_files.append(masks[idx_tp1])
            tp2skull_files.append(skulls[idx_tp2])
            tp2mask_files.append(masks[idx_tp2])
            tp1_subs.append(subject_id[idx_tp1])
            tp2_subs.append(subject_id[idx_tp2])

            tp1_files.append(t1s[idx_tp2])
            tp2_files.append(t1s[idx_tp1])
            tp1skull_files.append(skulls[idx_tp2])
            tp1mask_files.append(masks[idx_tp2])
            tp2skull_files.append(skulls[idx_tp1])
            tp2mask_files.append(masks[idx_tp1])
            tp1_subs.append(subject_id[idx_tp2])
            tp2_subs.append(subject_id[idx_tp1])

    return tp1_files, tp2_files, tp1mask_files, tp2mask_files, tp1skull_files, tp2skull_files, tp1_subs, tp2_subs


splitter = pe.JoinNode(niu.Function(input_names= ["subject_id", "t1_files",
                                                  "mask_files", "skull_files"],
                                    output_names= ["tp1_files", "tp2_files",
                                                   "tp1mask", "tp2mask",
                                                   "tp1skull", "tp2skull",
                                                   "tp1_subs", "tp2_subs"],
                                    function=pairwise_splitter),
                       name="pairwise_splitter",
                       joinfield=["subject_id",
                                  "t1_files",
                                  "mask_files",
                                  "skull_files"],
                       joinsource="inputspec")

wf.connect(inputspec, "subject_id", splitter, "subject_id")
#wf.connect(convert_to_nii, "out_file", splitter, "t1_files")
wf.connect(reo3, "out_file", splitter, "mask_files")
wf.connect(mask_skull, "out_file", splitter, "skull_files")
wf.connect(mask_t1, "out_file", splitter, "t1_files")

siena = pe.MapNode(SIENA(debug=True, bet_options="-f 0"),
                   iterfield=["in_file", "second_file",
                              "mask_file", "mask_file2",
                              "skull_file", "skull_file2"],
                   name="siena")
wf.connect(splitter, "tp1_files", siena, "in_file")
wf.connect(splitter, "tp2_files", siena, "second_file")
wf.connect(splitter, "tp1mask", siena, "mask_file")
wf.connect(splitter, "tp2mask", siena, "mask_file2")
wf.connect(splitter, "tp1skull", siena, "skull_file")
wf.connect(splitter, "tp2skull", siena, "skull_file2")

s2 = pe.Node(nio.DataSink(), name="sinker2")
s2.inputs.base_directory = sink
wf.connect(siena, "all_files", s2, "siena")

def get_subs(tp1_subs,tp2_subs):
    subs = []
    N = len(tp1_subs)
    for i in range(N)[::-1]:
        subs.append(("_siena%d"%i,"%s_%s" % (tp1_subs[i][:2], tp2_subs[i])))
    return subs

s2_subs = pe.Node(niu.Function(input_names=["tp1_subs","tp2_subs"],
                               output_names=["subs"],
                               function=get_subs),name="s2_subs")

wf.connect(splitter, "tp1_subs", s2_subs, "tp1_subs")
wf.connect(splitter, "tp2_subs", s2_subs, "tp2_subs")
wf.connect(s2_subs, "subs", s2, "substitutions")

wf.write_graph()

wf.run(plugin="MultiProc", plugin_args={"n_procs":4})
#plugin="SGE", plugin_args={"qsub_args":os.environ["PLUGIN_ARGS"]})
