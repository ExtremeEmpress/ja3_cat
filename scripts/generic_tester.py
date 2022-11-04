import ja3_converter as converter
import lda_ja3
import kmeans
import gensim
import pickle
import os
from gensim import corpora, models, similarities

data_path = "../data"
models_path = "../models"

lda_best_model = os.path.realpath("{}/lda_best_model".format(models_path))
lda_best_model_dict = os.path.realpath("{}/lda_best_model_dict".format(models_path))
kmeans_best_model = os.path.realpath("{}/kmeans_best_model".format(models_path))
kmeans_best_centroids = os.path.realpath("{}/kmeans_best_model_centroids".format(models_path))

# Import test JA3s
ja3s = converter.file_to_ja3s("{}/ja3_uniq_only.csv".format(data_path))

# Test LDA
print("Testing LDA (current best model)")
lda_model = models.LdaModel.load(lda_best_model)
dictionary = gensim.corpora.Dictionary.load(lda_best_model_dict)
indexes = lda_ja3.get_all_top_indexes(lda_model,dictionary,ja3s)
prod_to_i = converter.map_group_to_prod(indexes)
print(str(prod_to_i))
print()

# TEST KMEANS
kmeans_groups = 5
print("Testing K-means (current best model)")
kmeans_data = open(kmeans_best_model,"rb")
indexes = pickle.load(kmeans_data)
kmeans_data.close()
kmeans_centroids_data = open(kmeans_best_centroids,"rb")
centroids = pickle.load(kmeans_centroids_data)
kmeans_centroids_data.close()
prod_to_i2 = converter.map_group_to_prod(indexes)
print(str(prod_to_i2))
