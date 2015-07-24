__author__ = 'akeshavan'
import nipype.pipeline.engine as pe
import nipype.interfaces.io as nio
from glob import glob
import os
import nipype.interfaces.utility as niu

subject_list = [s.split("/")[-1][3:8] for s in sorted(glob("/data/henry7/keshavan/munich/data/f2_??_??.nii.gz"))]
print "list of subjects is", subject_list

working = "/data/henry_temp/keshavan/munich"
sink = "/data/henry7/keshavan/munich/analyses/ants_cortical_thickness"
subjects_dir="/data/henry7/keshavan/munich/analyses/surfaces"
data_dir = "/data/henry7/keshavan/munich/data"
scripts_dir = "/data/henry7/keshavan/munich/scripts"

#Run ants cortical thickness
wf = pe.Workflow(name="ants_cortical_thickness")
wf.base_dir = working

inputspec = pe.Node(niu.IdentityInterface(fields=["subject_id"]), name="inputspec")

inputspec.iterables = ("subject_id", subject_list)

datagrabber = pe.Node(nio.DataGrabber(infields=["subject_id"],
                                      outfields=["t1_filled"],
                                      sort_filelist=True),
                      name="datagrabber",
                      run_without_submitting=True)

datagrabber.inputs.template="*"
datagrabber.inputs.base_directory = data_dir
datagrabber.inputs.template_args = dict(t1_filled=[["subject_id"]])
datagrabber.inputs.field_template = dict(t1_filled="t1_%s_filled.nii.gz")

def cortical_thickness(t1_file, subject_id, template_home, sink_dir):
    import os
    cmd = "antsCorticalThickness.sh -d 3 -a {t1_file} -o {output_folder} -e \
{template_home}/OASIS-30_Atropos_template/T_template0.nii.gz \
-t {template_home}/OASIS-30_Atropos_template/T_template0_BrainCerebellum.nii.gz \
-m {template_home}/OASIS-30_Atropos_template/T_template0_BrainCerebellumProbabilityMask.nii.gz \
-f {template_home}/OASIS-30_Atropos_template/T_template0_BrainCerebellumExtractionMask.nii.gz \
-p {template_home}/OASIS-30_Atropos_template/Priors2/priors%d.nii.gz -k 1"

    output_folder = os.path.join(sink_dir, subject_id)+"/"
    cmd = cmd.format(t1_file=t1_file,
                     output_folder=output_folder,
                     template_home=template_home)
    print cmd
    os.system(cmd)
    if not os.path.exists(os.path.join(output_folder,"CorticalThickness.nii.gz")):
        raise Exception("Something did not run!")
    else:
        return output_folder


thickbrain = pe.Node(niu.Function(input_names=["t1_file", "subject_id", "template_home", "sink_dir"],
                                  output_names=[],
                                  function=cortical_thickness),
                     name="ants_cortical_thickness")
thickbrain.inputs.template_home = scripts_dir
thickbrain.inputs.sink_dir = sink

wf.connect(datagrabber, "t1_filled", thickbrain, "t1_file")
wf.connect(inputspec, "subject_id", datagrabber, "subject_id")
wf.connect(inputspec, "subject_id", thickbrain, "subject_id")

wf.run(plugin="SGE", plugin_args={"qsub_args": os.environ["PLUGIN_ARGS"]})


