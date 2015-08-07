export SUBJECTS_DIR=/data/henry7/keshavan/munich/analyses/surfaces/
cd $SUBJECTS_DIR
aparcstats2table --subjects ??_?? -d comma -t aparcstats_area_lh.csv --hemi lh --measure area --common-parcs 
aparcstats2table --subjects ??_?? -d comma -t aparcstats_area_rh.csv --hemi rh --measure area --common-parcs 
aparcstats2table --subjects ??_?? -d comma -t aparcstats_thickness_lh.csv --hemi lh --measure thickness --common-parcs 
aparcstats2table --subjects ??_?? -d comma -t aparcstats_thickness_rh.csv --hemi rh --measure thickness --common-parcs 
aparcstats2table --subjects ??_?? -d comma -t aparcstats_volume_lh.csv --hemi lh --measure volume --common-parcs 
aparcstats2table --subjects ??_?? -d comma -t aparcstats_volume_rh.csv --hemi rh --measure volume --common-parcs 
asegstats2table --subjects ??_?? -d comma -t asegstats.csv

aparcstats2table --subjects ??_??.long.?? -d comma -t aparcstats_area_lh.long.csv --hemi lh --measure area --common-parcs 
aparcstats2table --subjects ??_??.long.?? -d comma -t aparcstats_area_rh.long.csv --hemi rh --measure area --common-parcs 
aparcstats2table --subjects ??_??.long.?? -d comma -t aparcstats_thickness_lh.long.csv --hemi lh --measure thickness --common-parcs 
aparcstats2table --subjects ??_??.long.?? -d comma -t aparcstats_thickness_rh.long.csv --hemi rh --measure thickness --common-parcs 
aparcstats2table --subjects ??_??.long.?? -d comma -t aparcstats_volume_lh.long.csv --hemi lh --measure volume --common-parcs 
aparcstats2table --subjects ??_??.long.?? -d comma -t aparcstats_volume_rh.long.csv --hemi rh --measure volume --common-parcs 
asegstats2table --subjects ??_??.long.?? -d comma -t asegstats.long.csv
