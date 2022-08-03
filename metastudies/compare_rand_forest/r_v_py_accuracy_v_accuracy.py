#!/usr/bin/env python
# Author: Aaron Yerke, aaronyerke@gmail.com
# This is a script for comparing random forest output to pvalues
# --------------------------------------------------------------------------
print("Loading external libraries.",flush = True)
# --------------------------------------------------------------------------
import os, sys
import time
from statistics import mean
from matplotlib import markers
import math as math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
from sklearn.metrics import accuracy_score, roc_auc_score
import argparse
import random

# --------------------------------------------------------------------------
print("Reading commmandline input with optparse.", flush = True)
# --------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="This script runs a random forest test on various datasets.")
# parser.add_option("-f", "--file", dest="filename",
#                   help="write report to FILE", metavar="FILE")
parser.add_argument("-d", "--homedir",
                  default=os.path.expanduser(os.path.join("~", "git", "balance_tree_exploration")),
                  help="path to git balance treee exploration git repository", dest="homedir", metavar="homedir")
options, unknown = parser.parse_known_args()

# --------------------------------------------------------------------------
print("Establishing directory layout.", flush = True)
# --------------------------------------------------------------------------
home_dir = os.path.expanduser(options.homedir)
# projects = ["Vanderbilt", "Vangay", "Zeller", "Noguera-Julian"]
projects = ["Vanderbilt", "Vangay", "Zeller"]
output_dir = os.path.join(home_dir, "metastudies", "output")
assert os.path.exists(output_dir)
plot_pdf_fpath = os.path.join(output_dir, "inter_group_comp_R_v_Python_by_transformation.pdf")
# --------------------------------------------------------------------------
print("Establishing other constants.", flush = True)
# --------------------------------------------------------------------------
comp_ds = ['alr_DADA2', 'clr_DADA2', 'DaDa2', 'Filtered_IQtree', \
	'Filtered_IQtree_blw.sqrt_anorm', 'Filtered_Silva_DADA2', \
	'Filtered_Silva_DADA2_blw.sqrt_anorm', 'Filtered_UPGMA_DADA2', \
	'Filtered_UPGMA_DADA2_blw.sqrt_anorm', 'lognorm_DADA2', 'Silva_DADA2', \
	'Silva_DADA2_blw.sqrt_anorm']

pdf = matplotlib.backends.backend_pdf.PdfPages(plot_pdf_fpath)
#set font sizes
plt.rc('font', size=15) 
plt.rc('xtick', labelsize=20) 
plt.rc('ytick', labelsize=20) 
plt.rc('axes', labelsize=20) 
plt.rc('axes', titlesize=50)

for ds in comp_ds:
		print(ds)
		train_percent = 0.75
		pvals = {}
		r_score = {}
		py_score = {}
		features = []
		proj = []
		print(f"{ds}")
		for project in projects:
			print(f"Adding project {project}")
			main_output_label = f"sklearn_random_forest_manual_{train_percent}train_{project}_data"
			op_dir = os.path.join(home_dir, project, "output")
			result_fpath = os.path.join(op_dir, "tables", f"{main_output_label}.csv")
			print(result_fpath)
			my_table = pd.read_csv(result_fpath, sep=',', header=0)
			#table 1
			my_table = my_table.loc[my_table["dataset"] == ds,]
			# print(ds1_table)
			splits = my_table.columns[my_table.columns.str.startswith('split')].tolist()
			# print(my_table[splits].to_string())
			means = my_table[splits].agg(mean, axis = 1)
			print(means)
			# if any(pd.isna(my_table[splits])):
			# 	print("Nan found")
			# 	print(my_table[splits])
			# 	print(project)
			# 	sys.exit()
			assert not means.empty, f"{ds} is not in the py table from {project}"
			for feat, ave in zip(list(my_table["metadata"].values) ,list(means)):
				print(ave)
				py_score[feat] = ave
			#table 2
			# print("py_score")
			# print(py_score)
			op_dir = os.path.join(home_dir, project, "output")
			result_fpath = os.path.join(op_dir, "tables", f"wide_random_forest_score_R_20.csv")
			print("R tables")
			my_table = pd.read_csv(result_fpath, sep=',', header=0)
			print(my_table.to_string())
			my_table = my_table.loc[my_table["trans_group"] == ds,]
			print(my_table.to_string())
			splits = my_table.columns[my_table.columns.str.startswith('split')].tolist()
			means = my_table[splits].agg(mean, axis = 1)
			# assert not means.empty, f"{ds} is not in the table from {project}"
			# pval_fpath = os.path.join(op_dir, "tables", f"{project}_pValuesUnivariate_taxaVmetadata.csv")
			# my_table = pd.read_csv(pval_fpath, sep=',', header=0)
			print("R means")
			print(means)
			for feat, ave in zip(list(my_table["metadata_col"].values) ,list(means)):
				r_score[feat] = ave
				# pvals[feat] = min(my_table.loc[(my_table["meta_name"]==feat) & (my_table["taxa_lev"] == "Genus"), "pval"].values) + 1e-100
		same_keys = set(r_score.keys()).intersection(set(py_score.keys()))
		print("Same_keys")
		print(same_keys)
		print(r_score.keys())
		print(r_score.values())
		print(py_score.keys())
		print(py_score.values())
		r_score = {key:r_score[key] for key in same_keys}
		py_score = {key:py_score[key] for key in same_keys}
		print(r_score.keys())
		print(r_score.values())
		print(py_score.keys())
		print(py_score.values())
		ds1_lst = np.array(list(py_score.values()))
		ds2_lst = np.array(list(r_score.values()))
		print("build graphic")
		# a, b = np.polyfit(ds1_lst, ds2_lst, 1)
		fig = plt.figure(figsize=(11,11))
		fig.suptitle(f"Metastudy {train_percent}training {ds} Py vs R, accuracy vs accuracy")
		plt.subplots_adjust(bottom=0.8)
		ax = fig.add_subplot(1,1,1)
		# ax.scatter(ds1_lst, ds2_lst, label=list(r_score.keys()))
		ax.plot([0,1], [0,1], color = "r", label = "expected")
		# ax.plot(ds1_lst, a*ds1_lst+b, color = "green", label = "accuracy polyfit")
		ax.set_xlabel("Accuracy Python RF")
		ax.set_ylabel("Accuracy R RF")
		fig.tight_layout()
		for i, label in enumerate(list(r_score.keys())):
			ax.scatter(ds1_lst[i], ds2_lst[i], label=list(r_score.keys())[i])
			plt.annotate(label, (ds1_lst[i], ds2_lst[i]))
		ax.legend(title="Legend", loc="best", framealpha=0.1)
		print("Saving figure to pdf", flush = True)
		pdf.savefig( fig )
		# sys.exit()
		# print(my_table.columns)
		# print(sorted(set(my_table["dataset"].values),key=lambda s: s.lower()))

print("Saving pdf", flush = True)
pdf.close()
