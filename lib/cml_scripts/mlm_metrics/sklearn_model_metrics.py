#!/usr/bin/env python3

"""
Author: Aaron Yerke (aaronyerke@gmail.com)
For determining if PhILR weighting schemes improve any ML techniques.
This was useful: https://machinelearningmastery.com/compare-machine-learning-algorithms-python-scikit-learn/
Compare Algorithms
"""

# --------------------------------------------------------------------------
print("Loading external libraries.")
# --------------------------------------------------------------------------

import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
from pandas.api.types import is_string_dtype
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
import argparse

print("Running optparse.")

parser = argparse.ArgumentParser(description='Process some integers.')
# parser.add_option("-f", "--file", dest="filename",
#                   help="write report to FILE", metavar="FILE")
parser.add_argument("-m", "--metadata_cols",
                  action="store_false", dest="meta_col",
                  help="Metadata columns to analyse")
parser.add_argument("-d", "--homedir",
                  default=os.path.expanduser(os.path.join("~", "git", "balance_tree_exploration")), 
                  help="dataset dir path", dest="homedir", metavar="homedir")
parser.add_argument("-p", "--project", default="string",
                  help="project folder", metavar="project")
parser.add_argument("-a", "--use_all_meta", default=False,
                  help="use all metadata", metavar="use_all_meta")
parser.add_argument("-i", "--meta_index_col", default=0,
                  help="Name of column to use as row name for metadata", 
									metavar="meta_index_col")
                  
options, unknown = parser.parse_known_args()

print("Establishing directory layout.")
home_dir = options.homedir
project = options.project
output_dir = os.path.join(home_dir, project, "output")
silva_philr_dir = os.path.join(output_dir, "tables", "silva_philr_weights")
if not os.path.exists(silva_philr_dir):
  print(f"{silva_philr_dir} does not exist. Use silva_philr_weights.R to create it.")
  sys.exit()

print("Establishing other constants.")
main_output_label = "sklearn_ml_acc"
philr_part_weights = ["uniform","gm.counts","anorm","anorm.x.gm.counts","enorm","enorm.x.gm.counts"]
philr_ilr_weights = ["uniform","blw","blw.sqrt","mean.descendants"]
scoring = "accuracy"
col_names = ["metadata", "ilr_weight", "part_weight", "model", "split1", "split2", "split3", "split4", "split5", "split6", "split7", "split8", "split9", "split10"]
result_fpath = os.path.join(output_dir, "tables", f"{main_output_label}_{project}_data.csv")
pdf_fpath = os.path.join(output_dir, "graphics", f"bp_{main_output_label}_{project}.pdf")
algo_table_fpath = os.path.join(output_dir, "tables", f"algo_{main_output_label}_{project}.csv")

print("Importing data to working env.")
meta_df = pd.read_csv(os.path.join(home_dir, project, "patient_metadata.tsv"), sep='\t', header=0, index_col=options.meta_index_col)
if options.use_all_meta.lower() == "true":
  metad_cols = range(len(meta_df.columns))
else:
  metad_cols = options.meta_col

# prepare configuration for cross validation test harness
seed = 7
print("Preparing models.")
models = []
models.append(('LR', LogisticRegression()))
models.append(('LDA', LinearDiscriminantAnalysis()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('DTREE', DecisionTreeClassifier()))
models.append(('RF', RandomForestClassifier()))
models.append(('GausNB', GaussianNB()))
models.append(('SVM', SVC()))

# os.chdir(os.path.join(output_dir, "tables"))
# with open(result_fpath, "w+") as fl:
# 	fl.write(",".join(col_names))
# 	fl.write("\n")
# 	for pw in philr_part_weights:
# 		for iw in philr_ilr_weights:
# 			table_fn = f"ref_tree_cln_{iw}_{pw}.csv"
# 			my_df = pd.read_csv(os.path.join(silva_philr_dir, table_fn), sep=',', header=0, index_col=0)
# 			print("Dropping any extra values from metadata. Did it work?")
# 			meta_df = meta_df.loc[list(my_df.index.values)]
# 			print(list(my_df.index.values) == list(meta_df.index.values))
# 			for meta_c in metad_cols:
# 				m_c = list(meta_df.columns)[meta_c]
# 				# print(m_c)
# 				spetz_var = meta_df[m_c]#metadata var to test
# 				print(spetz_var.dtype)
# 				print(is_string_dtype(spetz_var))
# 				# if spetz_var.dtype.name == "object":
# 				if is_string_dtype(spetz_var) == True and spetz_var.isnull().sum() < 5:
# 					print("evaluate each model in turn.")
# 					for name, model in models:
# 						kfold = model_selection.KFold(n_splits=10, random_state=seed, shuffle=True)
# 						cv_results = model_selection.cross_val_score(model, my_df, spetz_var, cv=kfold, scoring=scoring)
# 						# result_str = np.array2string(cv_results, separator=",",suffix="/n")
# 						result_str = ",".join(map(str, cv_results.tolist()))
# 						msg = f"{m_c},{iw},{pw},{name},{result_str}\n"
# 						fl.write(msg)
# print("Finished recording accuracy.")
# #Setup for building boxplots
result_df = pd.read_csv(result_fpath, sep=',', header=0)
print(result_df.head())
pdf = matplotlib.backends.backend_pdf.PdfPages(pdf_fpath)
algos = sorted(set(result_df.loc[:,"model"]))
print(algos)
metadata_cats = set(result_df["metadata"])
print("metada_cats")
print(metadata_cats)
num_cols = 2
num_rows = abs(-len(algos)//num_cols)
print(result_df.head())

#For each metadata:
	# f_header = "metadata, m_mean, sd, LR_mean, LDA_mean, KNN_mean, DTREE_mean, RF_mean, GausNB_mean, SVM_mean"
	# f_header2 = "metadata, m_mean, m_sd, top_w, 2nd_w, 3rd_w"
	# metdata ave, st
	# for each w combo,
	#  	metada_weight_mean, metadata_weight_st, metadata_weight_rank 
	# for each algo: 
	# 	algo_mean, algo_std, algo_rank, mean for each w combo 
	# LR, LDA, KNN, DTREE, RF, GausNB, SVM

# LR, LDA, KNN, DTREE, RF, GausNB, SVM

# f_header = "metadata, mean, sd, top_algo, 2nd_algo, 3rd_algo"
# sample_header = f"{meta_c},{meta_mean},{meta_sd},{top_algo}"
print("Setup for table output")
# f_header = "metadata, m_mean, sd, LR_mean, LDA_mean, KNN_mean, DTREE_mean, RF_mean, GausNB_mean, SVM_mean"

f_header = ["feature","f_mean", "top_algo"].append(algos)
algo_header = ",".join(algos)

# print(f_header + algo_header)
algo_table  = pd.DataFrame(columns = f_header)

# with open(algo_table_fpath, "w+") as fl:
# 	fl.write(f"{f_header}{algo_header}\n")
for meta_c in metadata_cats:
	overall_mean = np.nanmean(result_df.iloc[:,4:])
	meta_result_df = pd.DataFrame(result_df[result_df["metadata"] == meta_c])
	overall_mean = np.nanmean(meta_result_df.iloc[:,5:])
	overall_sd = np.std(meta_result_df.iloc[:,5:], ddof=1)
	#for boxplot
	fig = plt.figure(figsize=(11,11))
	fig.suptitle(f"{project} PhILR weighting machine learning accuracy {meta_c}")
	plt.subplots_adjust(bottom=0.8)

	#for algo table
	# algo_table_line = [str(meta_c), str(overall_mean), str(overall_sd)]
	algo_means = dict()

	# algo_means["f_sd"] = overall_sd

	if not pd.isna(overall_mean):#don't proced if the data for the metadata is wonky
		for al in range(len(algos)):
			algo = algos[al]
			print(algo)
			fig_df = pd.DataFrame(meta_result_df[meta_result_df["model"] == algo])
			plot_data = fig_df.iloc[:,5:].transpose()
			print(f"df shape: {fig_df.shape[0]} {fig_df.shape[1]}")

			#for boxplot
			ax = fig.add_subplot(num_rows,num_cols, al +1)
			ax.boxplot(plot_data)
			ax.title.set_text(f"{algo} by weighting scheme")
			ax.axhline(np.nanmean(plot_data), c="r", linestyle="dashed")
			ax.axhline(overall_mean, c="g", linestyle = ("-."))
			ax.locator_params(axis='y', tight=True, nbins=4)
			new_labs = [f"{x}\n{y}" for x,y in zip(fig_df.loc[:,"ilr_weight"].values, fig_df.loc[:,"part_weight"].values)]
			# ax.set_xticklabels(fig_df.loc[:,"ilr_weight"].tolist(), rotation=90)
			ax.set_xticklabels(new_labs, rotation=90)
			ax.tick_params(axis='x', which='major', labelsize=6)

			#for algo table
			algo_means[algo] = np.nanmean(plot_data)

		#for boxplot
		fig.tight_layout()
		pdf.savefig( fig )
		
		#for algo table
		algo_means["top_algo"] = max(algo_means, key=algo_means.get)
		algo_means["feature"] = meta_c
		algo_means["f_mean"] = overall_mean
		algo_table = algo_table.append(algo_means, ignore_index=True)
		# max_algo = max(algo_means)
		# for algo in algos:
		# 	algo_table_line.append(algo_means.get(algo))
		# 	if algo == max_algo:
		# 		algo_table_line.append(f"{str(algo_means.get(algo))}^")
		# 	else:
		# 		algo_table_line.append(str(algo_means.get(algo)))
			# fl.write(",".join(algo_table_line))

pdf.close()
algo_table.to_csv(algo_table_fpath)
print("Python script completed.")


