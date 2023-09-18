#!/bin/bash
#SBATCH --partition=Orion                                    		# Partition/queue requested on server
#SBATCH --time=48:00:00                                      		# Time limit (hrs:min:sec)
#SBATCH --nodes=1                                         			# Number of nodes requested
#SBATCH --ntasks-per-node=1                          			# Number of CPUs (processor cores/tasks)
#SBATCH --mem=50gb                                          		# Memory limit

### Display the job context
echo Running on host: `hostname`
echo Using $SLURM_NTASKS processors across $SLURM_NNODES nodes

module load R
Rscript ~/git/lognorm_vs_CODA/lib/cml_scripts/transformations/p4_philr_transform.R -d ~/git/lognorm_vs_CODA -p Zeller

echo ""
echo "======================================================"
echo "End Time   : $(date)"
echo "======================================================"


