#!/bin/bash
#SBATCH --partition=Orion
#SBATCH --time=3:00:00
#SBATCH --nodes=1
#SBATCH --mem=12GB
#SBATCH --job-name=ZRunSra

cd ~/git/lognorm_vs_CODA

module load R
Rscript --vanilla Zeller/scripts/download_scripts/sra_download.R
