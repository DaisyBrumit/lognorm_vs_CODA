#!/bin/bash
#SBATCH --partition=Orion                                    		# Partition/queue requested on server
#SBATCH --job-name=Zeller_clustalo_iqtree                                   		# Job name
#SBATCH --time=48:00:00                                      		# Time limit (hrs:min:sec)
#SBATCH --nodes=6                                         			# Number of nodes requested
#SBATCH --ntasks-per-node=1                          			# Number of CPUs (processor cores/tasks)
#SBATCH --mem=50gb                                          		# Memory limit

### Display the job context
echo Job: $SLURM_JOB_NAME with ID $SLURM_JOB_ID
echo Running on host: `hostname`
echo Using $SLURM_NTASKS processors across $SLURM_NNODES nodes

srun bash ~/git/lognorm_vs_CODA/lib/cml_scripts/transformations/p5_make_iqtree.sh ~/git/lognorm_vs_CODA Zeller ~/git/lognorm_vs_CODA/Zeller/output/trees/ForwardReads_DADA2_taxonomy.aln

echo ""
echo "======================================================"
echo "End Time   : $(date)"
echo "======================================================"

