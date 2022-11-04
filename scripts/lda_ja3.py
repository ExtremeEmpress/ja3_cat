import ja3_distance
import ja3_converter as converter
import gensim
import numpy as np
#np.random.seed(1307)
import matplotlib.pyplot as plt
import re
import seaborn as sns

def corpsify_ja3s(ja3s):
    ja3s_to_w=[]
    for line in ja3s:
        ja3s_to_w.append(converter.ja3_to_words(line))

    dictionary = gensim.corpora.Dictionary(ja3s_to_w)

    bow_corpus = [dictionary.doc2bow(ja3) for ja3 in ja3s_to_w]
    return dictionary,bow_corpus

def create_model(ja3s,topics=10,rand=50):
    dictionary, bow_corpus = corpsify_ja3s(ja3s)

    lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=topics, id2word=dictionary, passes=100, workers=8, iterations=400, random_state=rand)

    return lda_model,dictionary,bow_corpus

def print_models(lda_model,bow_corpus,ja3s):
    dict,bow_c = corpsify_ja3s(ja3s)
    for w in bow_c:
        print(w)
        for index, score in sorted(lda_model[w], key=lambda tup: -1*tup[1]):
            print("\nindex: {}, score: {}\t \nTopic: {}".format(index, score, lda_model.print_topic(index, 10)))
            

def test_ja3s_f(lda_model,dictionary,test_ja3s):
    test_ja3s_w = []
    for ja3 in test_ja3s:
        test_ja3s_w.append(converter.ja3_to_words(ja3))

    print()
    for i in range(0,len(test_ja3s)):
        print("Test "+str(i))
        #print(test_ja3s[i])
        #print(converter.ja3_to_prod(test_ja3s[i]))
        bow_vector = dictionary.doc2bow(test_ja3s_w[i])
        for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
            print("index{}, score {}".format(index,score))
            #print("index{}, Score: {}\t Topic: {}".format(index, score, lda_model.print_topic(index, 10)))
        print()

# Return all indexes of JA3
def get_indexes(lda_model,dictionary,ja3):
    indexes = []
    ja3_w = converter.ja3_to_words(ja3)
    bow_vector = dictionary.doc2bow(ja3_w)
    for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
        indexes.append(index)
    return indexes

# Return top index of JA3
def get_top_index(lda_model,dictionary,ja3):
    top_index = ""
    ja3_w = converter.ja3_to_words(ja3)
    bow_vector = dictionary.doc2bow(ja3_w)
    index, score = sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1])[0]
    #print("index: {}, score: {}".format(index,score))
    return index

# Return all indexes of all provided JA3s
def get_all_indexes(lda_model,dictionary,ja3s):
    indexes = {}
    for ja3 in ja3s:
        indexes[ja3] = get_indexes(lda_model,dictionary,ja3)
    return indexes

# Return top index for all provided JA3s
def get_all_top_indexes(lda_model,dictionary,ja3s):
    indexes = {}
    for ja3 in ja3s:
        indexes[ja3] = get_top_index(lda_model,dictionary,ja3)
    return indexes

# Compare indexes of two JA3 values
def indexes_align(lda_model,dictionary,ja3_1,ja3_2):
    indexes_1 = get_indexes(lda_model,dictionary,ja3_1)
    indexes_2 = get_indexes(lda_model,dictionary,ja3_2)
    return indexes_1==indexes_2

# Compare top indexes of two JA3 values
def top_indexes_align(lda_model,dictionary,ja3_1,ja3_2):
    index_1 = get_top_index(lda_model,dictionary,ja3_1)
    index_2 = get_top_index(lda_model,dictionary,ja3_2)
    return index_1==index_2

# Calculate similarity of all indexes
def get_similarity(lda_model,dictionary,ja3s):
    if len(ja3s)==0:
        return 0
    similarity = 0
    indexes = []
    for ja3 in ja3s:
        indexes.append(get_indexes(lda_model,dictionary,ja3))
    #print(indexes)
    for i in range(0,len(indexes)):
        if indexes.count(indexes[i])-1 > similarity:
            similarity = similarity+1
        if similarity == len(indexes):
            return similarity/len(indexes)
    return similarity/len(indexes)

# Calculate similarity of top indexes
def get_top_similarity(lda_model,dictionary,ja3s):
    if len(ja3s)==0:
        return 0
    similarity = 0
    indexes = []
    for ja3 in ja3s:
        indexes.append(get_top_index(lda_model,dictionary,ja3))
    #print(indexes)
    for i in indexes:
        if indexes.count(i) > similarity:
            similarity = indexes.count(i)
        if similarity == len(indexes):
            return 1
    return similarity/len(indexes)

def plot_freq_bar(data_freq,filename,ori='h',nosort=False):
    if nosort:
        sorted_c = data_freq
    else:
        sorted_c = dict(sorted(data_freq.items(), key=lambda item: -item[1]))
    fig = plt.figure(1,figsize=(10,len(sorted_c)/4))
    if ori == 'h':
        sns.barplot(x=list(sorted_c.values()),y=list(sorted_c.keys()),orient=ori)
    elif ori == 'v':
        sns.barplot(x=list(sorted_c.keys()),y=list(sorted_c.values()),orient=ori)
    fig.subplots_adjust(left=0.48,bottom=0.3)
    fig.savefig(filename)
    plt.close(fig)
