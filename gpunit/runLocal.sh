
rm -rf job_1/*

docker run  -v ${PWD}:$PWD -w $PWD/job_1 genepattern/opencravat python /opencravat/opencravat_command_line.py -i $PWD/data/example_input -user $1 -pass $2 -ann1 clinvar,dbsnp  -assembly hg38
