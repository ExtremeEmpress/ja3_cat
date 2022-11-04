import argparse
import ja3_converter as converter
import gensim
import lda_ja3
import kmeans
from gensim import corpora, models, similarities
import os
import sys
import argparse
import pickle
import json

models_path = "../models"
data_path = "../data"
uniq_ja3s = converter.file_to_ja3s("{}/ja3_uniq_only.csv".format(data_path))

parser = argparse.ArgumentParser(description="A tool for querying which products have produced similar JA3 values as the one given as an argument. Choose the algorithm for categorization (LDA or K-Means).")
parser.add_argument("--model", help="The algorithm you want the results from (lda or kmeans).")
parser.add_argument("--ja3", help="The JA3 pre-hash string. Example: 771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172-156-157-47-53-10,0-23-65281-10-11-16-5-34-51-43-13-45-28-41,29-23-24-25-256-257,0")

args = parser.parse_args()

arg_ja3 = args.ja3
arg_model = args.model

if arg_model is None:
    parser.print_help()
    sys.exit(0)

if not arg_model == 'lda' and not arg_model == 'kmeans':
    print("Invalid model: select either lda or kmeans.")
    sys.exit(0)



    
print(converter.which_app(arg_model,arg_ja3))
