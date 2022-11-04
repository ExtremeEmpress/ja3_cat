import kmeans
import ja3_converter as converter
import math
import matplotlib.pyplot as plt
import pickle
import os
import sys
import argparse

data_path = "../data"
models_path = "../models"
min_topics = 1
max_topics = 20
iter = 100

parser = argparse.ArgumentParser(description="Finds the best K-Means model for current source material.")
parser.add_argument("--min", type=int, help="minimum amount of groups")
parser.add_argument("--max", type=int, help="maximum amount of groups")
parser.add_argument("--max_iter", type=int, help="maximum amount of iterations during K-Means")

args = parser.parse_args()

if args.min:
    min_topics = args.min
if args.max:
    max_topics = args.max
if args.max_iter:
    iter = args.max_iter

# Import source material
filename = "{}/ja3_uniq_only.csv".format(data_path)
with open(filename) as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]

# Import false positive test material
filename = "{}/fp_test.txt".format(data_path)
with open(filename) as file:
    fp_test_1 = file.readlines()
    fp_test_1 = [test.rstrip() for test in fp_test_1]
    
filename = "{}/fp_test_2.txt".format(data_path)
with open(filename) as file:
    fp_test_2 = file.readlines()
    fp_test_2 = [test.rstrip() for test in fp_test_2]

all_ff = converter.get_all_prods_from_ja3s(lines,"Firefox")
all_chrome = converter.get_all_prods_from_ja3s(lines,"Google Chrome")
all_windows = converter.get_all_prods_from_ja3s(lines,"Microsoft® Windows® Operating System")

ff_accur = []
c_accur = []
w_accur = []
overall_accur = []

bestness = 0
bestest_group_count = 0
bestest_indexes = []
bestest_centroids = []
bestest_overall_simil = 0
bestest_overall_fp = 1

print("Finding best amount of groups")
for i in range(min_topics,max_topics):
    print("Iteration {}".format(str(i)))
    indexes = {}
    indexes,centroids = kmeans.k_means(lines,i,iter)
    ff_simil=kmeans.get_top_similarity(indexes,all_ff)
    print("FF simil: {}".format(ff_simil))
    ff_accur.append([i,ff_simil])
    c_simil=kmeans.get_top_similarity(indexes,all_chrome)
    c_accur.append([i,c_simil])
    w_simil=kmeans.get_top_similarity(indexes,all_windows)
    w_accur.append([i,w_simil])
    overall_simil=(ff_simil+c_simil+w_simil)/3 # ff, chrome and windows
    overall_accur.append([i,overall_simil])
    fp_simil_1=kmeans.get_top_similarity(indexes,fp_test_1)
    fp_simil_2=kmeans.get_top_similarity(indexes,fp_test_2)
    overall_fp=(fp_simil_1+fp_simil_2)/2
    if overall_fp==0:
        if overall_simil-overall_fp > bestness:
            bestness = overall_simil-overall_fp
            bestest_indexes = indexes
            bestest_centroids = centroids
            bestest_group_count = i
            bestest_overall_simil = overall_simil
            bestest_overall_fp = overall_fp
        print("Overall similarity: {}, False positive rate: {}".format(str(overall_simil),str(overall_fp)))

if bestest_group_count == 0:
    print("No model was found to satisfy the minimum false positive requirement.")
    sys.exit(0)

print("Best topic count: {} with overall similarity of {} and false positive match of {}".format(bestest_group_count,bestest_overall_simil,bestest_overall_fp))

# Store found model
bestest_fn = "{}/best_kmeans_{}_groups.pkl".format(models_path,bestest_group_count)
bestest_centroids_fn = "{}/best_kmeans_{}_centroids.pkl".format(models_path,bestest_group_count)
bestest_file = open(bestest_fn,"wb")
pickle.dump(bestest_indexes,bestest_file)
bestest_file.close()
bestest_c_file = open(bestest_centroids_fn,"wb")
pickle.dump(bestest_centroids,bestest_c_file)
bestest_c_file.close()

# Update symlink to latest model
bestest_model_symlink = "{}/kmeans_best_model".format(models_path)
bestest_centroids_symlink = "{}/kmeans_best_model_centroids".format(models_path)
if os.path.exists(bestest_model_symlink):
    os.unlink(bestest_model_symlink)
os.symlink(bestest_fn, bestest_model_symlink)
if os.path.exists(bestest_centroids_symlink):
    os.unlink(bestest_centroids_symlink)
os.symlink(bestest_centroids_fn, bestest_centroids_symlink)

with open("output_kmeans_model_finder_accuracy", 'a') as out:
    out.write('Firefox accuracies: \n\n')
    out.write(str(ff_accur) + '\n\n')
    out.write('Chrome accuracies: \n\n')
    out.write(str(c_accur) + '\n\n')
    out.write('Windows accuracies: \n\n')
    out.write(str(w_accur) + '\n\n')
    out.write('All  accuracies: \n\n')
    out.write(str(overall_accur) + '\n\n')
