#!/bin/bash

#SBATCH --partition=Orion                                    		# Partition/queue requested on server
#SBATCH --job-name=run_p2_denovo_tree_UPGMA_Zeller     		# Job name
#SBATCH --time=24:00:00                                      		# Time limit (hrs:min:sec)
#SBATCH --nodes=1                                         			# Number of nodes requested
#SBATCH --ntasks-per-node=1                          			# Number of CPUs (processor cores/tasks)
#SBATCH --mem=50gb                                          		# Memory limit
#SBATCH --mail-type=BEGIN,END,FAIL                              	# Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=amyerke@uncc.edu                            	# Specified email address
#SBATCH --output=/users/amyerke/slurmLogs/%x.%j.out     # Set directory for standard output
#SBATCH --error=/users/amyerke/slurmLogs/%x.%j.out      # Set directory for error log
##SBATCH --uid=amyerke
#SBATCH --get-user-env

### Display the job context
echo Job: $SLURM_JOB_NAME with ID $SLURM_JOB_ID
echo Running on host: `hostname`
echo Using $SLURM_NTASKS processors across $SLURM_NNODES nodes

module load R

Rscript ~/git/lognorm_vs_CODA/lib/cml_scripts/transformations/p2_denovo_tree_UPGMA.R \
--homedir ~/git/lognorm_vs_CODA \
--project Zeller \
--metadata ~/git/lognorm_vs_CODA/Zeller/patient_metadata.csv \
--metadata_delim , \
--metadata_rowname Run \
--input_table filtered_90prcnt_dada2.rds \
--output_file_prefix filtered_90prcnt \
--alignment_file filtered_90prcnt_aln.rds

# Options:
# 	-d CHARACTER, --homedir=CHARACTER
# 		dataset dir path
# 
# 	-p CHARACTER, --project=CHARACTER
# 		project folder
# 
# 	-m CHARACTER, --metadata=CHARACTER
# 		metadata file path with filename
# 
# 	-l CHARACTER, --metadata_delim=CHARACTER
# 		metadata file deliminator
# 
# 	-r CHARACTER, --metadata_rowname=CHARACTER
# 		metadata file row to use for row names
# 
# 	-s CHARACTER, --outputfilesuffix=CHARACTER
# 		output_file_suffix
# 
# 	-f NUMERIC, --filter_level=NUMERIC
# 		taxonimic level for making otu table 1-6
# 
# 	-i INPUT_TABLE, --input_table=INPUT_TABLE
# 		input file name, must be in project/r_objects/
# 
# 	-x OUTPUTPREFIX, --output_file_prefix=OUTPUTPREFIX
# 		output_file_prefix
# 
# 	-a ALGNMNT, --alignment_file=ALGNMNT
# 		alignment file, should be an R object in output/r_objects/
# 
# 	-h, --help
# 		Show this help message and exit

echo ""
echo "======================================================"
echo "End Time   : $(date)"
echo "======================================================"
