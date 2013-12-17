#!/bin/bash -xe

# INPUTS
director_src="../conpaas-director/cpsdirector"
services_src="../conpaas-services/src/conpaas"
director_title='ConPaaS director API'
services_title='ConPaaS managers API'

# OUTPUTS
dest_dir="gen_api"
latex_dir="$dest_dir/latex"
odt_dir="$dest_dir/odt"

# COMMAND LOCATION
cps_api="./src/cps_api/cps_api.py"


#### main ####

mkdir -p "$dest_dir"
mkdir -p "$latex_dir"
mkdir -p "$odt_dir"

director_basename="director"
services_basename="services"

director_rst="$dest_dir/$director_basename.rst"
services_rst="$dest_dir/$services_basename.rst"

python "$cps_api" --title="$director_title" "$director_src" > "$director_rst"
python "$cps_api" --title="$services_title" "$services_src" > "$services_rst"

rst2odt --report=4 "$director_rst" > "$odt_dir/$director_basename.odt"
rst2latex --report=4 "$director_rst" > "$latex_dir/$director_basename.tex"

rst2odt --report=4 "$services_rst" > "$odt_dir/$services_basename.odt"
rst2latex --report=4 "$services_rst" > "$latex_dir/$services_basename.tex"

# generate the pdf file from the generated LaTeX, 3 times to solve cross-references
cd "$latex_dir"
pdflatex "$director_basename.tex" > /dev/null && pdflatex "$director_basename.tex" > /dev/null && pdflatex "$director_basename.tex" > /dev/null
pdflatex "$services_basename.tex" > /dev/null && pdflatex "$services_basename.tex" > /dev/null && pdflatex "$services_basename.tex" > /dev/null
cd ..

