import lda_ja3
import ja3_converter as converter
import math
import matplotlib.pyplot as plt
import pandas as pd
import re
import seaborn as sns
import ja3_distance
import os
import argparse
from collections import Counter
from pathlib import Path
import json
import sys

current_path = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.normpath("{}/../data".format(current_path))
graphs_path = os.path.normpath("{}/../graphs".format(current_path))
models_path = os.path.normpath("{}/../models".format(current_path))

filename = "{}/ja3_uniq_only.csv".format(data_path)
filetype = "png"

parser = argparse.ArgumentParser(description="Graphify your TLS data! This script takes as input a path to a file containing a list of JA3 pre-hash strings. Graphs will be generated under {}.\n\nIf no filepath is given, the default file will be used ({}).".format(os.path.realpath("{}/<filename>/".format(models_path)),filename))
parser.add_argument("--filepath", help="Path to a file containing a list of JA3 pre-hash strings, one value per line.", nargs='?')
parser.add_argument("--filetype", help="Filetype of the exported images. Available: png, pdf. Default: png.", nargs='?')

args = parser.parse_args()

if args.filepath:
    filename = args.filepath
    if re.search('^/',filename)==None:
        print("Provide full path to the input file.")
        sys.exit(2)

if args.filetype:
    filetype = args.filetype
    if re.search('^(png|pdf)$',filetype)==None:
        print("Available file types: png, pdf.")
        sys.exit(2)
        
with open(filename) as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]

words_freq,ciph_freq,ext_freq,groups_freq,formats_freq = converter.get_ja3_frequencies(lines)

ja3_prods_lda = {}
ja3_prods_kmeans = {}
app_counter_lda = {}
app_counter_kmeans = {}
lda_groups = {}
kmeans_groups = {}
for line in lines:
    lda_prods = json.loads(converter.which_app("lda",line))
    kmeans_prods = json.loads(converter.which_app("kmeans",line))
    ja3_prods_lda[line]=lda_prods["category"]
    ja3_prods_kmeans[line]=kmeans_prods["category"]
    key = ','.join(lda_prods["category"])
    if not key in lda_groups:
        lda_groups[key] = 1
    else:
        lda_groups[key] += 1
    key2 = ','.join(kmeans_prods["category"])
    if not key2 in kmeans_groups:
        kmeans_groups[key2] = 1
    else:
        kmeans_groups[key2] += 1
    for cat in lda_prods["category"]:
        if not cat in app_counter_lda:
            app_counter_lda[cat] = 1
        else:
            app_counter_lda[cat] += 1
    for cat in kmeans_prods["category"]:
        if not cat in app_counter_kmeans:
            app_counter_kmeans[cat] = 1
        else:
            app_counter_kmeans[cat] += 1

all_ff_lda = []
all_ff_kmeans = []
all_chrome_lda = []
all_chrome_kmeans = []
all_windows_lda = []
all_windows_kmeans = []
all_others_lda = []
all_others_kmeans = []
for ja3_l in ja3_prods_lda:
    id = False
    if "Firefox" in ja3_prods_lda[ja3_l]:
        all_ff_lda.append(ja3_l)
        id = True
    if "Google Chrome" in ja3_prods_lda[ja3_l]:
        all_chrome_lda.append(ja3_l)
        id = True
    if "Microsoft® Windows® Operating System" in ja3_prods_lda[ja3_l]:
        all_windows_lda.append(ja3_l)
        id = True
    if not id:
        all_others_lda.append(ja3_l)

for ja3_k in ja3_prods_kmeans:
    id = False
    if "Firefox" in ja3_prods_kmeans[ja3_k]:
        all_ff_kmeans.append(ja3_k)
        id = True
    if "Google Chrome" in ja3_prods_kmeans[ja3_k]:
        all_chrome_kmeans.append(ja3_k)
        id = True
    if "Microsoft® Windows® Operating System" in ja3_prods_kmeans[ja3_k]:
        all_windows_kmeans.append(ja3_k)
        id = True
    if not id:
        all_others_kmeans.append(ja3_k)

dirname = Path(filename).stem
graphsdir = os.path.realpath("{}/{}".format(graphs_path,dirname))
lda_path = "{}/lda".format(graphsdir)
kmeans_path = "{}/kmeans".format(graphsdir)

        
if not os.path.exists(graphsdir):
    os.mkdir(graphsdir)
    os.mkdir(lda_path)
    os.mkdir(kmeans_path)
else:
    if not os.path.isdir(graphsdir):
        print("A file exists already at {}, cannot create directory for graphs with same name. Exiting.".format(graphsdir))
        sys.exit(2)
    else:
        print("The folder for the graphs already exists in {} - existing graphs will be overridden.".format(graphsdir))
        if not os.path.exists(lda_path):
            os.mkdir(lda_path)
        if not os.path.exists(kmeans_path):
            os.mkdir(kmeans_path)

lda_ja3.plot_freq_bar(ciph_freq,"{}/all_ciphers.{}".format(graphsdir,filetype))
lda_ja3.plot_freq_bar(ext_freq,"{}/all_extensions.{}".format(graphsdir,filetype))
lda_ja3.plot_freq_bar(groups_freq,"{}/all_groups.{}".format(graphsdir,filetype))
lda_ja3.plot_freq_bar(formats_freq,"{}/all_formats.{}".format(graphsdir,filetype))

# Print for Kmeans:

# Print specific graphs for Firefox, Chrome, Windows and Others

if not all_ff_kmeans == []:
    ff_words_freq_kmeans,ff_ciph_freq_kmeans,ff_ext_freq_kmeans,ff_groups_freq_kmeans,ff_formats_freq_kmeans = converter.get_ja3_frequencies(all_ff_kmeans)
    lda_ja3.plot_freq_bar(ff_ciph_freq_kmeans,"{}/firefox_ciphers_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(ff_ext_freq_kmeans,"{}/firefox_extensions_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(ff_groups_freq_kmeans,"{}/firefox_groups_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(ff_formats_freq_kmeans,"{}/firefox_formats_kmeans.{}".format(kmeans_path,filetype))

if not all_chrome_kmeans == []:
    c_words_freq_kmeans,c_ciph_freq_kmeans,c_ext_freq_kmeans,c_groups_freq_kmeans,c_formats_freq_kmeans = converter.get_ja3_frequencies(all_chrome_kmeans)
    lda_ja3.plot_freq_bar(c_ciph_freq_kmeans,"{}/chrome_ciphers_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(c_ext_freq_kmeans,"{}/chrome_extensions_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(c_groups_freq_kmeans,"{}/chrome_groups_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(c_formats_freq_kmeans,"{}/chrome_formats_kmeans.{}".format(kmeans_path,filetype))

if not all_windows_kmeans == []:
    w_words_freq_kmeans,w_ciph_freq_kmeans,w_ext_freq_kmeans,w_groups_freq_kmeans,w_formats_freq_kmeans = converter.get_ja3_frequencies(all_windows_kmeans)
    lda_ja3.plot_freq_bar(w_ciph_freq_kmeans,"{}/windows_ciphers_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(w_ext_freq_kmeans,"{}/windows_extensions_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(w_groups_freq_kmeans,"{}/windows_groups_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(w_formats_freq_kmeans,"{}/windows_formats_kmeans.{}".format(kmeans_path,filetype))

if not all_others_kmeans == []:
    o_words_freq_kmeans,o_ciph_freq_kmeans,o_ext_freq_kmeans,o_groups_freq_kmeans,o_formats_freq_kmeans = converter.get_ja3_frequencies(all_others_kmeans)
    lda_ja3.plot_freq_bar(o_ciph_freq_kmeans,"{}/other_ciphers_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(o_ext_freq_kmeans,"{}/other_extensions_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(o_groups_freq_kmeans,"{}/other_groups_kmeans.{}".format(kmeans_path,filetype))
    lda_ja3.plot_freq_bar(o_formats_freq_kmeans,"{}/other_formats_kmeans.{}".format(kmeans_path,filetype))

# Print graphs plotting data as coordinates

ff_coord = ja3_distance.ja3s_to_coords(all_ff_kmeans)
chrome_coord = ja3_distance.ja3s_to_coords(all_chrome_kmeans)
win_coord = ja3_distance.ja3s_to_coords(all_windows_kmeans)

ja3_distance.plot_scatter("Firefox", "Google Chrome", all_ff_kmeans, all_chrome_kmeans, 1, 3, "{}/scatter_ciph_groups_firefox_chrome_kmeans.{}".format(kmeans_path,filetype))
ja3_distance.plot_scatter("Firefox", "Google Chrome", all_ff_kmeans, all_chrome_kmeans, 1, 2, "{}/scatter_ciph_extensions_firefox_chrome_kmeans.{}".format(kmeans_path,filetype))
ja3_distance.plot_scatter("Firefox", "Google Chrome", all_ff_kmeans, all_chrome_kmeans, 2, 3, "{}/scatter_extensions_groups_firefox_chrome_kmeans.{}".format(kmeans_path,filetype))
ja3_distance.plot_scatter("Firefox", "Google Chrome", all_ff_kmeans, all_chrome_kmeans, 1, 4, "{}/scatter_ciph_formats_firefox_chrome_kmeans.{}".format(kmeans_path,filetype))
ja3_distance.plot_scatter("Firefox", "Google Chrome", all_ff_kmeans, all_chrome_kmeans, 2, 4, "{}/scatter_extensions_formats_firefox_chrome_kmeans.{}".format(kmeans_path,filetype))
ja3_distance.plot_scatter("Firefox", "Google Chrome", all_ff_kmeans, all_chrome_kmeans, 3, 4, "{}/scatter_groups_formats_firefox_chrome_kmeans.{}".format(kmeans_path,filetype))

ja3_distance.plot_scatter("Firefox", "Windows", all_ff_kmeans, all_windows_kmeans, 1, 3, "{}/scatter_ciph_groups_firefox_windows_kmeans.{}".format(kmeans_path,filetype))
ja3_distance.plot_scatter("Firefox", "Windows", all_ff_kmeans, all_windows_kmeans, 1, 2, "{}/scatter_ciph_extensions_firefox_windows_kmeans.{}".format(kmeans_path,filetype))
ja3_distance.plot_scatter("Firefox", "Windows", all_ff_kmeans, all_windows_kmeans, 2, 3, "{}/scatter_extensions_groups_firefox_windows_kmeans.{}".format(kmeans_path,filetype))

ja3_distance.plot_scatter("Chrome", "Windows", all_chrome_kmeans, all_windows_kmeans, 1, 3, "{}/scatter_ciph_groups_chrome_windows_kmeans.{}".format(kmeans_path,filetype))
ja3_distance.plot_scatter("Chrome", "Windows", all_chrome_kmeans, all_windows_kmeans, 1, 2, "{}/scatter_ciph_extensions_chrome_windows_kmeans.{}".format(kmeans_path,filetype))
ja3_distance.plot_scatter("Chrome", "Windows", all_chrome_kmeans, all_windows_kmeans, 2, 3, "{}/scatter_extensions_groups_chrome_windows_kmeans.{}".format(kmeans_path,filetype))

ja3_distance.plot_scatter_three("Chrome", "Firefox", "Windows", all_chrome_kmeans, all_ff_kmeans, all_windows_kmeans, 1, 2, "{}/scatter_ciph_extensions_chrome_firefox_windows_kmeans.{}".format(kmeans_path,filetype))
ja3_distance.plot_scatter_three("Chrome", "Firefox", "Windows", all_chrome_kmeans, all_ff_kmeans, all_windows_kmeans, 1, 3, "{}/scatter_ciph_groups_chrome_firefox_windows_kmeans.{}".format(kmeans_path,filetype))
ja3_distance.plot_scatter_three("Chrome", "Firefox", "Windows", all_chrome_kmeans, all_ff_kmeans, all_windows_kmeans, 2, 3, "{}/scatter_extensions_groups_chrome_firefox_windows_kmeans.{}".format(kmeans_path,filetype))

# Print for LDA:

# Print specific graphs for Firefox, Chrome, Windows and Others

if not all_ff_lda == []:
    ff_words_freq_lda,ff_ciph_freq_lda,ff_ext_freq_lda,ff_groups_freq_lda,ff_formats_freq_lda = converter.get_ja3_frequencies(all_ff_lda)
    lda_ja3.plot_freq_bar(ff_ciph_freq_lda,"{}/firefox_ciphers_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(ff_ext_freq_lda,"{}/firefox_extensions_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(ff_groups_freq_lda,"{}/firefox_groups_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(ff_formats_freq_lda,"{}/firefox_formats_lda.{}".format(lda_path,filetype))

if not all_chrome_lda == []:
    c_words_freq_lda,c_ciph_freq_lda,c_ext_freq_lda,c_groups_freq_lda,c_formats_freq_lda = converter.get_ja3_frequencies(all_chrome_lda)
    lda_ja3.plot_freq_bar(c_ciph_freq_lda,"{}/chrome_ciphers_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(c_ext_freq_lda,"{}/chrome_extensions_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(c_groups_freq_lda,"{}/chrome_groups_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(c_formats_freq_lda,"{}/chrome_formats_lda.{}".format(lda_path,filetype))

if not all_windows_lda == []:
    w_words_freq_lda,w_ciph_freq_lda,w_ext_freq_lda,w_groups_freq_lda,w_formats_freq_lda = converter.get_ja3_frequencies(all_windows_lda)
    lda_ja3.plot_freq_bar(w_ciph_freq_lda,"{}/windows_ciphers_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(w_ext_freq_lda,"{}/windows_extensions_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(w_groups_freq_lda,"{}/windows_groups_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(w_formats_freq_lda,"{}/windows_formats_lda.{}".format(lda_path,filetype))

if not all_others_lda == []:
    o_words_freq_lda,o_ciph_freq_lda,o_ext_freq_lda,o_groups_freq_lda,o_formats_freq_lda = converter.get_ja3_frequencies(all_others_lda)
    lda_ja3.plot_freq_bar(o_ciph_freq_lda,"{}/other_ciphers_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(o_ext_freq_lda,"{}/other_extensions_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(o_groups_freq_lda,"{}/other_groups_lda.{}".format(lda_path,filetype))
    lda_ja3.plot_freq_bar(o_formats_freq_lda,"{}/other_formats_lda.{}".format(lda_path,filetype))

# Print graphs plotting data as coordinates

ff_coord = ja3_distance.ja3s_to_coords(all_ff_lda)
chrome_coord = ja3_distance.ja3s_to_coords(all_chrome_lda)
win_coord = ja3_distance.ja3s_to_coords(all_windows_lda)

ja3_distance.plot_scatter("Firefox", "Google Chrome", all_ff_lda, all_chrome_lda, 1, 3, "{}/scatter_ciph_groups_firefox_chrome_lda.{}".format(lda_path,filetype))
ja3_distance.plot_scatter("Firefox", "Google Chrome", all_ff_lda, all_chrome_lda, 1, 2, "{}/scatter_ciph_extensions_firefox_chrome_lda.{}".format(lda_path,filetype))
ja3_distance.plot_scatter("Firefox", "Google Chrome", all_ff_lda, all_chrome_lda, 2, 3, "{}/scatter_extensions_groups_firefox_chrome_lda.{}".format(lda_path,filetype))
ja3_distance.plot_scatter("Firefox", "Windows", all_ff_lda, all_windows_lda, 1, 3, "{}/scatter_ciph_groups_firefox_windows_lda.{}".format(lda_path,filetype))
ja3_distance.plot_scatter("Firefox", "Windows", all_ff_lda, all_windows_lda, 1, 2, "{}/scatter_ciph_extensions_firefox_windows_lda.{}".format(lda_path,filetype))
ja3_distance.plot_scatter("Firefox", "Windows", all_ff_lda, all_windows_lda, 2, 3, "{}/scatter_extensions_groups_firefox_windows_lda.{}".format(lda_path,filetype))
ja3_distance.plot_scatter("Chrome", "Windows", all_chrome_lda, all_windows_lda, 1, 3, "{}/scatter_ciph_groups_chrome_windows_lda.{}".format(lda_path,filetype))
ja3_distance.plot_scatter("Chrome", "Windows", all_chrome_lda, all_windows_lda, 1, 2, "{}/scatter_ciph_extensions_chrome_windows_lda.{}".format(lda_path,filetype))
ja3_distance.plot_scatter("Chrome", "Windows", all_chrome_lda, all_windows_lda, 2, 3, "{}/scatter_extensions_groups_chrome_windows_lda.{}".format(lda_path,filetype))

ja3_distance.plot_scatter_three("Chrome", "Firefox", "Windows", all_chrome_lda, all_ff_lda, all_windows_lda, 1, 2, "{}/scatter_ciph_extensions_chrome_firefox_windows_lda.{}".format(lda_path,filetype))
ja3_distance.plot_scatter_three("Chrome", "Firefox", "Windows", all_chrome_lda, all_ff_lda, all_windows_lda, 1, 3, "{}/scatter_ciph_groups_chrome_firefox_windows_lda.{}".format(lda_path,filetype))
ja3_distance.plot_scatter_three("Chrome", "Firefox", "Windows", all_chrome_lda, all_ff_lda, all_windows_lda, 2, 3, "{}/scatter_extensions_groups_chrome_firefox_windows_lda.{}".format(lda_path,filetype))

# Print app graphs

counts = Counter(lines)

amount_kmeans = {"Firefox":0,"Chrome":0,"Windows":0,"Other":0}
amount_lda = {"Firefox":0,"Chrome":0,"Windows":0,"Other":0}
for ja3 in counts:
    if ja3 in all_ff_kmeans:
        amount_kmeans["Firefox"] += counts[ja3]
    if ja3 in all_chrome_kmeans:
        amount_kmeans["Chrome"] += counts[ja3]
    if ja3 in all_windows_kmeans:
        amount_kmeans["Windows"] += counts[ja3]
    if ja3 in all_others_kmeans:
        amount_kmeans["Other"] += counts[ja3]

    if ja3 in all_ff_lda:
        amount_lda["Firefox"] += counts[ja3]
    if ja3 in all_chrome_lda:
        amount_lda["Chrome"] += counts[ja3]
    if ja3 in all_windows_lda:
        amount_lda["Windows"] += counts[ja3]
    if ja3 in all_others_lda:
        amount_lda["Other"] += counts[ja3]

lda_ja3.plot_freq_bar(amount_kmeans,"{}/app_amounts_kmeans.{}".format(graphsdir,filetype),'h',True)
lda_ja3.plot_freq_bar(amount_lda,"{}/app_amounts_lda.{}".format(graphsdir,filetype),'h',True)

lda_ja3.plot_freq_bar(app_counter_kmeans,"{}/all_app_amounts_kmeans.{}".format(graphsdir,filetype))
lda_ja3.plot_freq_bar(app_counter_lda,"{}/all_app_amounts_lda.{}".format(graphsdir,filetype))

pretty_kmeans_groups = {}
pretty_lda_groups = {}

# NOTE! Below, "(None)" means that no product in sample set
# got the same index as this JA3 value.

for k, v in kmeans_groups.items():
    klist = list(k.split(","))
    if 'Google Chrome' in klist:
        prettyk = "Google Chrome,"
        klist.remove("Google Chrome")
        prettyk += ','.join(klist[0:1])
    elif 'Microsoft® Windows® Operating System' in klist:
        prettyk = "Microsoft Windows,"
        klist.remove("Microsoft® Windows® Operating System")
        prettyk += ','.join(klist[0:1])
    else:
        prettyk = ','.join(klist[0:2])
    if len(klist) > 2:
        prettyk+=",etc."
    if prettyk == "":
        prettyk = "(None)"
    pretty_kmeans_groups[prettyk] = v

for k, v in lda_groups.items():
    klist = list(k.split(","))
    if 'Google Chrome' in klist:
        prettyk = "Google Chrome,"
        klist.remove("Google Chrome")
        prettyk += ','.join(klist[0:1])
    elif 'Microsoft® Windows® Operating System' in klist:
        prettyk = "Microsoft Windows,"
        klist.remove("Microsoft® Windows® Operating System")
        prettyk += ','.join(klist[0:1])
    else:
        prettyk = ','.join(klist[0:2])
    if len(klist) > 2:
        prettyk+=",etc."
    if prettyk == "":
        prettyk = "(None)"
    pretty_lda_groups[prettyk] = v
    
lda_ja3.plot_freq_bar(pretty_kmeans_groups,"{}/app_groups_kmeans.{}".format(graphsdir,filetype))
lda_ja3.plot_freq_bar(pretty_lda_groups,"{}/app_groups_lda.{}".format(graphsdir,filetype))


