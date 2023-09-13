# make db out of tree fasta
# useful rescources:
#  https://www.ncbi.nlm.nih.gov/books/NBK279688/
module load blast

cd ~/git/lognorm_vs_CODA/lib/ref_tree_objs

# remove any possible duplicate values in treeFasta.fasta
awk 'BEGIN {i = 1;} { if ($1 ~ /^>/) { tmp = h[i]; h[i] = $1; } else if (!a[$1]) { s[i] = $1; a[$1] = "1"; i++; } else { h[i] = tmp; } } END { for (j = 1; j < i; j++) { print h[j]; print s[j]; } }' treeFasta.fasta > treeFastaout.fasta

# -parse_seqids option is required to keep the original sequence identifiers. Otherwise makeblastdb will generate its own identifiers.
makeblastdb -in treeFasta.fasta -out db/tree -parse_seqids -dbtype nucl

# [amyerke@cph-i1 tree_prep]$ makeblastdb -in fixed_treeFasta.fasta -out db/tree -parse_seqids -dbtype nucl
# 
# Building a new DB, current time: 06/07/2020 15:09:52
# New DB name:   /users/amyerke/git/Western_gut/tree_prep/db/tree
# New DB title:  fixed_treeFasta.fasta
# Sequence type: Nucleotide
# Keep MBits: T
# Maximum file size: 1000000000B
# Adding sequences from FASTA; added 13900 sequences in 3.87929 seconds.
