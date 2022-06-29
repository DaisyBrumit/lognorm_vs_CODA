#!/usr/bin/env python
# Author: Aaron Yerke, aaronyerke@gmail.com
# This is a script for assessing the various compositional data 
# transformations against the random forest
# --------------------------------------------------------------------------
print("Loading external libraries.",flush = True)
# --------------------------------------------------------------------------
import os, sys
from statistics import mean
from matplotlib import markers
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
import matplotlib.colors as mcolors
from pandas.api.types import is_string_dtype
from requests import head
from sklearn import model_selection
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, roc_auc_score
import argparse
import random

# --------------------------------------------------------------------------
print("Reading commmandline input with optparse.", flush = True)
# --------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="This script runs a random forest test on various datasets.")
# parser.add_option("-f", "--file", dest="filename",
#                   help="write report to FILE", metavar="FILE")
parser.add_argument("-m", "--metadata_cols",
                  action="store_false", dest="meta_col",
                  help="Metadata columns to analyse")
parser.add_argument("-d", "--homedir",
                  default=os.path.expanduser(os.path.join("~", "git", "balance_tree_exploration")),
                  help="path to git balance treee exploration git repository", dest="homedir", metavar="homedir")
parser.add_argument("-p", "--project", default="string",
                  help="project folder", metavar="project")
parser.add_argument("-a", "--use_all_meta", default=False,
                  help="use all metadata", metavar="use_all_meta")
parser.add_argument("-f", "--metada_fn", default="string", dest="meta_fn",
                  help="Name of file at the top of the project folder to use as metadata.", 
									metavar="meta_fn")
parser.add_argument("-l", "--delimiter", default="\t",
                  help="File delimiting symbol for metadata. Default is tab.",
									metavar="delim", dest="delim")
parser.add_argument("-i", "--meta_index_col", default=0,
                  help="Name of column to use as row name for metadata",
                  metavar="meta_index_col", dest="meta_index_col")
parser.add_argument("-t", "--training", default=0.9,
                  help="Percentating of table to use for training. The rest will be used for testing.",
                  metavar="training", dest="training")

options, unknown = parser.parse_known_args()

# --------------------------------------------------------------------------
print("Establishing directory layout.", flush = True)
# --------------------------------------------------------------------------
home_dir = os.path.expanduser(options.homedir)
project = options.project
output_dir = os.path.join(home_dir, project, "output")
assert os.path.exists(output_dir)

def df_factory(my_path, my_sep):
	try:
		df = pd.read_csv(my_path, sep=my_sep, header=0, index_col=0)
		return df
	except Exception as e:
		print(f"An exception occurred during creation of dataframe from {my_path}", flush = True)
		print(e, flush=True)
		sys.exit(f"There was a problem loading {my_path}")

# --------------------------------------------------------------------------
print("Establishing other constants", flush = True)
# --------------------------------------------------------------------------
seed = 7
scoring = "Accuracy"
train_percent = options.training
main_output_label = f"sklearn_random_forest_manual_{train_percent}train_{project}_data"
result_fpath = os.path.join(output_dir, "tables", f"{main_output_label}.csv")
col_names = ["dataset", "metadata"]
num_iterations = 10
col_names = col_names + [f"split{x}" for x in range(num_iterations)]
print(col_names)
pdf_fpath = os.path.join(output_dir, "graphics", f"bp_{main_output_label}.pdf")

# --------------------------------------------------------------------------
print("Importing data to working env.", flush = True)
# --------------------------------------------------------------------------
meta_df = pd.read_csv(os.path.expanduser(os.path.join(home_dir, project, str(options.meta_fn))), \
	sep=options.delim, header=0, index_col=options.meta_index_col)
metad_cols = range(len(meta_df.columns))
print(meta_df.dtypes, flush=True)
meta_df = meta_df.select_dtypes(["object", "category", "string"])
#Commented code for scrambling the rownames
# # meta_df.head
# # meta_df = meta_df.sample(frac=1)
# # meta_df.head

# ----------------------------------------------------------------------------
print("Setting up tables to feed the random forest model.", flush = True)
# --------------------------------------------------------------------------
tables = []
tables.append(("DaDa2",(os.path.join(output_dir, "tables", "ForwardReads_DADA2.txt"),"\t"),"r"))
# tables.append(("HashSeq", (os.path.join(output_dir,  "hashseq", "hashseq.csv"),","), "r"))
tables.append(("lognorm_DADA2", (os.path.join(output_dir, "tables", "lognorm_dada2.csv"), ","), "y"))
# tables.append(("lognorm_HashSeq", (os.path.join(output_dir,"tables", "lognorm_hashseq.csv"), ","), "y"))
tables.append(("alr_DADA2", (os.path.join(output_dir, "tables", "alr_asv.csv"), ","), "g"))
# tables.append(("alr_HashSeq", (os.path.join(output_dir,"tables", "alr_hashseq.csv"), ","), "g"))
tables.append(("clr_DADA2", (os.path.join(output_dir, "tables", "clr_asv.csv"), ","), "g"))
# tables.append(("clr_HashSeq", (os.path.join(output_dir,"tables", "clr_hashseq.csv"), ","), "m"))
tables.append(("Silva_ref_counts_only", (os.path.join(output_dir,"tables", "Silva_ref_counts.csv"), ","), "k"))

print(len(tables), flush = True)
philr_part_weights = ["anorm","enorm"]
philr_ilr_weights = ["blw.sqrt","mean.descendants"]
silva_philr_dir = os.path.join(output_dir, "tables", "silva_philr_weights")
if not os.path.exists(silva_philr_dir):
  print(f"{silva_philr_dir} does not exist. Use PhILR_random_trees_and_counts_tables.R to create it.", flush = True)
  sys.exit()
for pw in philr_part_weights:
	for iw in philr_ilr_weights:
		table_fn = f"ref_tree_cln_{iw}_{pw}.csv"
		my_df = pd.read_csv(os.path.join(silva_philr_dir, table_fn), sep=',', header=0, index_col=0)
		my_label = f"ref_tree_philr_{iw}_{pw}"
		tables.append((my_label, (os.path.join(silva_philr_dir, table_fn), ','), "w"))

# --------------------------------------------------------------------------
print(f"Running random forest model to find {scoring}.", flush = True)
# --------------------------------------------------------------------------
with open(result_fpath, "w+") as fl:
	fl.write(",".join(col_names))
	fl.write("\n")
	for meta_c in metad_cols:
		m_c = list(meta_df.columns)[meta_c]
		# meta_df = meta_df.loc[list(my_table.index.values)
		for name, table_info, color in tables:
			my_table = df_factory(table_info[0], table_info[1])
			my_accuracy = [0] * num_iterations
			random.seed(10)
			for i in range(num_iterations):
				rand_int = random.randint(0, 1000)
				respns_var = meta_df.loc[list(my_table.index.values),m_c]#metadata var to test
				pred_train, pred_test, resp_train, resp_test = model_selection.train_test_split(my_table, respns_var, train_size=float(train_percent), random_state=rand_int, shuffle=True) 
				if is_string_dtype(respns_var) == True and respns_var.isnull().sum() < 5:
					clf = RandomForestClassifier(max_depth=2, random_state=0)
					clf.fit(pred_train, resp_train)
					resp_pred = clf.predict(pred_test)
					# if len(set(respns_var)) <= 2:
					# 	resp_pred = list(x[0:len(resp_pred[1])-1] for x in resp_pred)
					# my_accuracy[i] = roc_auc_score(y_true = resp_test, y_score=resp_pred, multi_class="ovr", average="weighted")
					my_accuracy[i] = accuracy_score(resp_test, resp_pred)
			final_acc = ",".join(map(str, my_accuracy))
			print(final_acc)
			msg = f"{name},{m_c},{final_acc}\n"
			print(msg)
			fl.write(msg)
		print(f"{name}, {m_c} mean is: {mean(my_accuracy)}", flush = True)
print("Finished recording accuracy.", flush = True)

# --------------------------------------------------------------------------
print(f"Building boxplot PDF.", flush = True)
# --------------------------------------------------------------------------
#Setup for building boxplots
result_df = pd.read_csv(result_fpath, sep=',', header=0, index_col=0)
metadata_cats = list(set(result_df["metadata"]))
num_cols = 2
num_rows = abs(-len(tables)//num_cols)

pdf = matplotlib.backends.backend_pdf.PdfPages(pdf_fpath)
for meta_c in metadata_cats:
	fig = plt.figure(figsize=(11,11))
	fig.suptitle(f"{project} random forest manual {train_percent}training {scoring} {meta_c}")
	plt.subplots_adjust(bottom=0.8)
	meta_result_df = pd.DataFrame(result_df[result_df["metadata"] == meta_c])
	# flat_num_only = pd.DataFrame(meta_result_df.iloc[:,5:]).to_numpy().flatten()
	plot_data = meta_result_df.iloc[:,1:].transpose()
	f_mean = np.nanmean(plot_data)
	ax = fig.add_subplot(1,1,1)
	bp = ax.boxplot(plot_data, patch_artist = True, labels=plot_data.columns)
	colors = list([sublist[-1] for sublist in tables])
	for patch, color in zip(bp['boxes'], colors):
		patch.set_facecolor(color)
	ax.axhline(np.nanmean(plot_data), c="r", linestyle="dashed")
	ax.axhline(f_mean, c="g", linestyle = ("-."))
	ax.set_xticklabels(labels = plot_data.columns, rotation=90)
	ax.tick_params(axis='x', which='major', labelsize=15)

	#for boxplot
	fig.tight_layout()
	pdf.savefig( fig )

print("Saving pdf", flush = True)
pdf.close()
