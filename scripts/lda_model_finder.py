import lda_ja3
import ja3_converter as converter
import math
import matplotlib.pyplot as plt
import os
import sys
import numpy as np
import argparse

data_path = "../data"
models_path = "../models"
min_topics = 5
max_topics = 6
rand_iter = 4

parser = argparse.ArgumentParser(description="Finds the best LDA model for current source material.")
parser.add_argument("--min", type=int, help="minimum amount of topics")
parser.add_argument("--max", type=int, help="maximum amount of topics")
parser.add_argument("--rand_iterate", type=int, help="iterations with different rand numbers for LDA model")

args = parser.parse_args()

if args.min:
    min_topics = args.min
if args.max:
    max_topics = args.max
if args.rand_iterate:
    rand_iter = args.rand_iterate

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
bestest_topic_count = 0
bestest_model = ""
bestest_dict = ""
bestest_bow_corpus = ""
bestest_overall_simil = 0
bestest_overall_fp = 1
bestest_rand = 0

print("Finding best amount of topics")
for i in range(min_topics,max_topics):
    print("LDA iteration {}".format(str(i)))
    # Iterate through several random numbers to get a better accuracy
    rand_bestness = 0
    rand_fp = 1
    rand_bestest_model = ""
    rand_bestest_dict = ""
    rand_bestest_bow_corpus = ""
    rand_bestest_overall_simil = 0
    rand_bestest_overall_fp = 1
    rand_bestest_rand = 0
    for j in range(1,rand_iter+1):
        rand = np.random
        print("Random iteration {}".format(str(j)))
        lda_model,dictionary,bow_corpus = lda_ja3.create_model(lines,topics=i,rand=rand)
        ff_rand_simil=lda_ja3.get_top_similarity(lda_model,dictionary,all_ff)
        c_rand_simil=lda_ja3.get_top_similarity(lda_model,dictionary,all_chrome)
        w_rand_simil=lda_ja3.get_top_similarity(lda_model,dictionary,all_windows)
        overall_rand_simil=(ff_rand_simil+c_rand_simil+w_rand_simil)/3 # ff, chrome and windows
        fp_rand_simil_1=lda_ja3.get_top_similarity(lda_model,dictionary,fp_test_1)
        fp_rand_simil_2=lda_ja3.get_top_similarity(lda_model,dictionary,fp_test_2)
        overall_rand_fp=(fp_rand_simil_1+fp_rand_simil_2)/2
        if overall_rand_simil-overall_rand_fp > rand_bestness:
                    rand_bestness = overall_rand_simil-overall_rand_fp
                    rand_bestest_model = lda_model
                    rand_bestest_dict = dictionary
                    rand_bestest_bow_corpus = bow_corpus
                    rand_bestest_overall_simil = overall_rand_simil
                    rand_bestest_overall_fp = overall_rand_fp
                    rand_bestest_rand = rand
        if not rand_bestest_model == "":
            ff_simil=lda_ja3.get_top_similarity(rand_bestest_model,rand_bestest_dict,all_ff)
            ff_accur.append([i,ff_simil])
            c_simil=lda_ja3.get_top_similarity(rand_bestest_model,rand_bestest_dict,all_chrome)
            c_accur.append([i,c_simil])
            w_simil=lda_ja3.get_top_similarity(rand_bestest_model,rand_bestest_dict,all_windows)
            w_accur.append([i,w_simil])
            overall_simil=(ff_simil+c_simil+w_simil)/3 # ff, chrome and windows
            overall_accur.append([i,overall_simil])
            fp_simil_1=lda_ja3.get_top_similarity(rand_bestest_model,rand_bestest_dict,fp_test_1)
            fp_simil_2=lda_ja3.get_top_similarity(rand_bestest_model,rand_bestest_dict,fp_test_2)
            overall_fp=(fp_simil_1+fp_simil_2)/2
            if overall_simil-overall_fp > bestness:
                bestness = overall_simil-overall_fp
                bestest_model = rand_bestest_model
                bestest_dict = rand_bestest_dict
                bestest_bow_corpus = rand_bestest_bow_corpus
                bestest_topic_count = i
                bestest_rand = rand_bestest_rand
                bestest_overall_simil = overall_simil
                bestest_overall_fp = overall_fp
            print("Overall similarity: {}, False positive rate: {}".format(str(overall_simil),str(overall_fp)))

if bestest_topic_count == 0:
    print("No model was found to satisfy the minimum false positive requirement.")
    sys.exit(0)

print("Best topic count: {} with overall similarity of {} and false positive match of {}".format(bestest_topic_count,bestest_overall_simil,bestest_overall_fp))

# Store found model
bestest_model_fn = "{}/best_lda_{}_topics.model".format(models_path,bestest_topic_count)
bestest_dict_fn = "{}/best_lda_{}_dict.model".format(models_path,bestest_topic_count)
bestest_model.save(bestest_model_fn)
bestest_dict.save(bestest_dict_fn)

# Update symlink to latest model
bestest_model_symlink = "{}/lda_best_model".format(models_path)
bestest_dict_symlink = "{}/lda_best_model_dict".format(models_path)
if os.path.exists(bestest_model_symlink):
    os.unlink(bestest_model_symlink)
if os.path.exists(bestest_dict_symlink):
    os.unlink(bestest_dict_symlink)
os.symlink(bestest_model_fn, bestest_model_symlink)
os.symlink(bestest_dict_fn, bestest_dict_symlink)

with open("output_lda_model_finder_accuracy", 'a') as out:
    out.write('Firefox accuracies: \n\n')
    out.write(str(ff_accur) + '\n\n')
    out.write('Chrome accuracies: \n\n')
    out.write(str(c_accur) + '\n\n')
    out.write('Windows accuracies: \n\n')
    out.write(str(w_accur) + '\n\n')
    out.write('All  accuracies: \n\n')
    out.write(str(overall_accur) + '\n\n')
