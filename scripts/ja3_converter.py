from collections import Counter
import numpy as np
import ja3_distance
import lda_ja3
import kmeans
import re
import os
import gensim
from gensim import models
import json
import pickle

current_path = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.normpath("{}/../data".format(current_path))
models_path = os.path.normpath("{}/../models".format(current_path))
prod_to_ja3_f = "{}/prod_ja3.csv".format(data_path)

prod_ja3 = {}
ja3_prod = {}

def file_to_ja3s(file):
    lines= open(file).readlines()
    lines = [line.rstrip() for line in lines]
    return lines

lines = file_to_ja3s(prod_to_ja3_f)
for line in lines:
    prod,rest = line.split(',',1)
    rest = rest.split('"',3)[1]
    if not prod in prod_ja3:
        prod_ja3[prod] = []
    prod_ja3[prod].append(rest)
    if not rest in ja3_prod:
        ja3_prod[rest] = []
    ja3_prod[rest].append(prod)

def ja3_to_prod(ja3):
    return ja3_prod[ja3]

def prod_to_ja3(prod):
    if prod in prod_ja3:
        return prod_ja3[prod]
    else:
        return None

def all_prods():
    return list(prod_ja3.keys())

# Return dict of prod -> ja3s where
# ja3s will contain all ja3 values
# in the input list that have been
# produced by prod
def list_prods_for_ja3s(ja3s):
    prod_ja3s = {}
    for ja3 in ja3s:
        prods = ja3_to_prod(ja3)
        for prod in prods:
            if not prod in prod_ja3s:
                prod_ja3s[prod]=[]
            prod_ja3s[prod].append(ja3)
    return prod_ja3s

def get_all_prods_from_ja3s(ja3s,prod):
    ja3_list = []
    for ja3 in ja3s:
        if prod in ja3_to_prod(ja3):
            ja3_list.append(ja3)

    return ja3_list

def ja3_to_words(ja3):
    ja3_arr = ja3_distance.arrify_ja3(ja3)
    ja3_words = []
    for i in range(0,5):
        for c in ja3_arr[i]:
            if i==0:
                ja3_words.append("v"+str(c))
            elif i==1:
                ja3_words.append("c"+str(c))
            elif i==2:
                ja3_words.append("e"+str(c))
            elif i==3:
                ja3_words.append("g"+str(c))
            elif i==4:
                ja3_words.append("f"+str(c))
    return ja3_words

def ja3_to_separate_wordlists(ja3):
    ja3_arr = ja3_distance.arrify_ja3(ja3)
    ja3_version = []
    ja3_ciphers = []
    ja3_extensions = []
    ja3_groups = []
    ja3_formats = []
    for i in range(0,5):
        for c in ja3_arr[i]:
            if i==0:
                ja3_version.append(str(c))
            elif i==1:
                ja3_ciphers.append(str(c))
            elif i==2:
                ja3_extensions.append(str(c))
            elif i==3:
                ja3_groups.append(str(c))
            elif i==4:
                ja3_formats.append(str(c))
    return ja3_version,ja3_ciphers,ja3_extensions,ja3_groups,ja3_formats

# Map results of arbitrary grouping algorithm
# into product. Return a dict which gives the
# most common index (group) for each product
# (mapping of prod -> most common index).
# result will have product: index mappings.
# indexes should contain a dict of ja3: index(es)
# One ja3 can be mapped to several indexes, but
# the first one will be considered the most important one.
def map_group_to_prod(indexes):
    ja3s = indexes.keys()
    prod_ja3s = list_prods_for_ja3s(ja3s)
    prod_to_index={}
    for prod in prod_ja3s: 
        prod_indexes = []
        for ja3 in prod_ja3s[prod]:
            if type(indexes[ja3]) is np.int64 or type(indexes[ja3]) is int:
                prod_indexes.append(indexes[ja3])
            else:
                for index in indexes[ja3]:
                    prod_indexes.append(index)
        #print("Indexes for {}: {}".format(prod,str(prod_indexes)))
        c = Counter(prod_indexes)
        #print("Most common index for {} was {}".format(prod,c.most_common(1)[0][0]))
        prod_to_index[prod] = c.most_common(1)[0][0]
    return prod_to_index

uniq_ja3s = file_to_ja3s("{}/ja3_uniq_only.csv".format(data_path))

# Returns a list of products that get the same index in the sample set for an arbitrary
# grouping algorithm. indexes should contain a dict of ja3: index(es)
def prods_with_index(indexes,index):
    prods = []
    prod_map = map_group_to_prod(indexes)
    for prod in prod_map.keys():
        if prod_map[prod] == index:
            prods.append(prod)
    return prods

def get_ja3_frequencies(ja3s):
    ciph_r = re.compile("^c(.*)$")
    ext_r = re.compile("^e(.*)$")
    gro_r = re.compile("^g(.*)$")
    for_r = re.compile("^f(.*)$")
    words_freq = {}
    ciph_freq = {}
    ext_freq = {}
    groups_freq = {}
    formats_freq = {}
    dict,bow = lda_ja3.corpsify_ja3s(ja3s)
    for k in dict.cfs:
        words_freq[dict[k]]=dict.cfs[k]
        if ciph_r.match(dict[k]):
            if int(ciph_r.match(dict[k]).group(1)) in ciphers:
                name=ciphers[int(ciph_r.match(dict[k]).group(1))]
            
            else:
                name="unknown("+ciph_r.match(dict[k]).group(1)+")"
            ciph_freq[name]=dict.cfs[k]
        elif ext_r.match(dict[k]):
            if ext_r.match(dict[k]).group(1)=="":
                name="no extensions"
            elif int(ext_r.match(dict[k]).group(1)) in extensions:
                name=extensions[int(ext_r.match(dict[k]).group(1))]
            else:
                name="unknown("+ext_r.match(dict[k]).group(1)+")"
            ext_freq[name]=dict.cfs[k]
        elif gro_r.match(dict[k]):
            if gro_r.match(dict[k]).group(1)=="":
                name="no supported groups"
            elif int(gro_r.match(dict[k]).group(1)) in groups:
                name=groups[int(gro_r.match(dict[k]).group(1))]
            else:
                name="unknown("+gro_r.match(dict[k]).group(1)+")"
            groups_freq[name]=dict.cfs[k]
        elif for_r.match(dict[k]):
            if for_r.match(dict[k]).group(1)=="":
                name="no ec point formats"
            elif int(for_r.match(dict[k]).group(1)) in formats:
                name=formats[int(for_r.match(dict[k]).group(1))]
            else:
                name="unknown("+for_r.match(dict[k]).group(1)+")"
            formats_freq[name]=dict.cfs[k]
    return words_freq,ciph_freq,ext_freq,groups_freq,formats_freq

def which_app(model,ja3):
    if model == "lda":
        lda_best_model = os.path.realpath("{}/lda_best_model".format(models_path))
        lda_best_model_dict = os.path.realpath("{}/lda_best_model_dict".format(models_path))
        lda_model = models.LdaModel.load(lda_best_model)
        dictionary = gensim.corpora.Dictionary.load(lda_best_model_dict)

        index = lda_ja3.get_top_index(lda_model,dictionary,ja3)
        indexes = lda_ja3.get_all_top_indexes(lda_model,dictionary,uniq_ja3s)
        prods = prods_with_index(indexes,index)
        return json.dumps({"model":model,"category":prods})

    if model == "kmeans":
        kmeans_best_model = os.path.realpath("{}/kmeans_best_model".format(models_path))
        kmeans_best_centroids = os.path.realpath("{}/kmeans_best_model_centroids".format(models_path))
        kmeans_data = open(kmeans_best_model,"rb")
        indexes = pickle.load(kmeans_data)
        kmeans_data.close()
        kmeans_centroids_data = open(kmeans_best_centroids,"rb")
        centroids = pickle.load(kmeans_centroids_data)
        kmeans_centroids_data.close()
        index,dist,centroid = kmeans.get_index(centroids, ja3)
        prods = prods_with_index(indexes,index)
        if prods == []:
            prods = ja3_to_prod(centroid)
        return json.dumps({"model":model,"category":prods,"distance":dist})

ciphers = {
    0x00:"TLS_NULL_WITH_NULL_NULL",
    0x01:"TLS_RSA_WITH_NULL_MD5",
    0x02:"TLS_RSA_WITH_NULL_SHA",
    0x03:"TLS_RSA_EXPORT_WITH_RC4_40_MD5",
    0x04:"TLS_RSA_WITH_RC4_128_MD5",
    0x05:"TLS_RSA_WITH_RC4_128_SHA",
    0x06:"TLS_RSA_EXPORT_WITH_RC2_CBC_40_MD5",
    0x07:"TLS_RSA_WITH_IDEA_CBC_SHA",
    0x08:"TLS_RSA_EXPORT_WITH_DES40_CBC_SHA",
    0x09:"TLS_RSA_WITH_DES_CBC_SHA",
    0x0a:"TLS_RSA_WITH_3DES_EDE_CBC_SHA",
    0x0b:"TLS_DH_DSS_EXPORT_WITH_DES40_CBC_SHA",
    0x0c:"TLS_DH_DSS_WITH_DES_CBC_SHA",
    0x0d:"TLS_DH_DSS_WITH_3DES_EDE_CBC_SHA",
    0x0e:"TLS_DH_RSA_EXPORT_WITH_DES40_CBC_SHA",
    0x0f:"TLS_DH_RSA_WITH_DES_CBC_SHA",
    0x10:"TLS_DH_RSA_WITH_3DES_EDE_CBC_SHA",
    0x11:"TLS_DHE_DSS_EXPORT_WITH_DES40_CBC_SHA",
    0x12:"TLS_DHE_DSS_WITH_DES_CBC_SHA",
    0x13:"TLS_DHE_DSS_WITH_3DES_EDE_CBC_SHA",
    0x14:"TLS_DHE_RSA_EXPORT_WITH_DES40_CBC_SHA",
    0x15:"TLS_DHE_RSA_WITH_DES_CBC_SHA",
    0x16:"TLS_DHE_RSA_WITH_3DES_EDE_CBC_SHA",
    0x17:"TLS_DH_anon_EXPORT_WITH_RC4_40_MD5",
    0x18:"TLS_DH_anon_WITH_RC4_128_MD5",
    0x19:"TLS_DH_anon_EXPORT_WITH_DES40_CBC_SHA",
    0x1a:"TLS_DH_anon_WITH_DES_CBC_SHA",
    0x1b:"TLS_DH_anon_WITH_3DES_EDE_CBC_SHA",
    0x1c:"SSL_FORTEZZA_KEA_WITH_NULL_SHA",
    0x1d:"SSL_FORTEZZA_KEA_WITH_FORTEZZA_CBC_SHA",
    0x1e:"SSL_FORTEZZA_KEA_WITH_RC4_128_SHA",
    0x1e:"TLS_KRB5_WITH_DES_CBC_SHA",
    0x1f:"TLS_KRB5_WITH_3DES_EDE_CBC_SHA",
    0x20:"TLS_KRB5_WITH_RC4_128_SHA",
    0x21:"TLS_KRB5_WITH_IDEA_CBC_SHA",
    0x22:"TLS_KRB5_WITH_DES_CBC_MD5",
    0x23:"TLS_KRB5_WITH_3DES_EDE_CBC_MD5",
    0x24:"TLS_KRB5_WITH_RC4_128_MD5",
    0x25:"TLS_KRB5_WITH_IDEA_CBC_MD5",
    0x26:"TLS_KRB5_EXPORT_WITH_DES_CBC_40_SHA",
    0x27:"TLS_KRB5_EXPORT_WITH_RC2_CBC_40_SHA",
    0x28:"TLS_KRB5_EXPORT_WITH_RC4_40_SHA",
    0x29:"TLS_KRB5_EXPORT_WITH_DES_CBC_40_MD5",
    0x2a:"TLS_KRB5_EXPORT_WITH_RC2_CBC_40_MD5",
    0x2b:"TLS_KRB5_EXPORT_WITH_RC4_40_MD5",
    0x2c:"TLS_PSK_WITH_NULL_SHA",
    0x2d:"TLS_DHE_PSK_WITH_NULL_SHA",
    0x2e:"TLS_RSA_PSK_WITH_NULL_SHA",
    0x2f:"TLS_RSA_WITH_AES_128_CBC_SHA",
    0x30:"TLS_DH_DSS_WITH_AES_128_CBC_SHA",
    0x31:"TLS_DH_RSA_WITH_AES_128_CBC_SHA",
    0x32:"TLS_DHE_DSS_WITH_AES_128_CBC_SHA",
    0x33:"TLS_DHE_RSA_WITH_AES_128_CBC_SHA",
    0x34:"TLS_DH_anon_WITH_AES_128_CBC_SHA",
    0x35:"TLS_RSA_WITH_AES_256_CBC_SHA",
    0x36:"TLS_DH_DSS_WITH_AES_256_CBC_SHA",
    0x37:"TLS_DH_RSA_WITH_AES_256_CBC_SHA",
    0x38:"TLS_DHE_DSS_WITH_AES_256_CBC_SHA",
    0x39:"TLS_DHE_RSA_WITH_AES_256_CBC_SHA",
    0x3a:"TLS_DH_anon_WITH_AES_256_CBC_SHA",
    0x3b:"TLS_RSA_WITH_NULL_SHA256",
    0x3c:"TLS_RSA_WITH_AES_128_CBC_SHA256",
    0x3d:"TLS_RSA_WITH_AES_256_CBC_SHA256",
    0x3e:"TLS_DH_DSS_WITH_AES_128_CBC_SHA256",
    0x3f:"TLS_DH_RSA_WITH_AES_128_CBC_SHA256",
    0x40:"TLS_DHE_DSS_WITH_AES_128_CBC_SHA256",
    0x41:"TLS_RSA_WITH_CAMELLIA_128_CBC_SHA",
    0x42:"TLS_DH_DSS_WITH_CAMELLIA_128_CBC_SHA",
    0x43:"TLS_DH_RSA_WITH_CAMELLIA_128_CBC_SHA",
    0x44:"TLS_DHE_DSS_WITH_CAMELLIA_128_CBC_SHA",
    0x45:"TLS_DHE_RSA_WITH_CAMELLIA_128_CBC_SHA",
    0x46:"TLS_DH_anon_WITH_CAMELLIA_128_CBC_SHA",
    0x60:"TLS_RSA_EXPORT1024_WITH_RC4_56_MD",
    0x61:"TLS_RSA_EXPORT1024_WITH_RC2_CBC_56_MD",
    0x62:"TLS_RSA_EXPORT1024_WITH_DES_CBC_SH",
    0x63:"TLS_DHE_DSS_EXPORT1024_WITH_DES_CBC_SH",
    0x64:"TLS_RSA_EXPORT1024_WITH_RC4_56_SH",
    0x65:"TLS_DHE_DSS_EXPORT1024_WITH_RC4_56_SH",
    0x66:"TLS_DHE_DSS_WITH_RC4_128_SH",
    0x67:"TLS_DHE_RSA_WITH_AES_128_CBC_SHA256",
    0x68:"TLS_DH_DSS_WITH_AES_256_CBC_SHA256",
    0x69:"TLS_DH_RSA_WITH_AES_256_CBC_SHA256",
    0x6a:"TLS_DHE_DSS_WITH_AES_256_CBC_SHA256",
    0x6b:"TLS_DHE_RSA_WITH_AES_256_CBC_SHA256",
    0x6c:"TLS_DH_anon_WITH_AES_128_CBC_SHA256",
    0x6d:"TLS_DH_anon_WITH_AES_256_CBC_SHA256",
    0x80:"TLS_GOSTR341094_WITH_28147_CNT_IMIT",
    0x81:"TLS_GOSTR341001_WITH_28147_CNT_IMI",
    0x82:"TLS_GOSTR341001_WITH_NULL_GOSTR341",
    0x83:"TLS_GOSTR341094_WITH_NULL_GOSTR341",
    0x84:"TLS_RSA_WITH_CAMELLIA_256_CBC_SHA",
    0x85:"TLS_DH_DSS_WITH_CAMELLIA_256_CBC_SHA",
    0x86:"TLS_DH_RSA_WITH_CAMELLIA_256_CBC_SHA",
    0x87:"TLS_DHE_DSS_WITH_CAMELLIA_256_CBC_SHA",
    0x88:"TLS_DHE_RSA_WITH_CAMELLIA_256_CBC_SHA",
    0x89:"TLS_DH_anon_WITH_CAMELLIA_256_CBC_SHA",
    0x8a:"TLS_PSK_WITH_RC4_128_SHA",
    0x8b:"TLS_PSK_WITH_3DES_EDE_CBC_SHA",
    0x8c:"TLS_PSK_WITH_AES_128_CBC_SHA",
    0x8d:"TLS_PSK_WITH_AES_256_CBC_SHA",
    0x8e:"TLS_DHE_PSK_WITH_RC4_128_SHA",
    0x8f:"TLS_DHE_PSK_WITH_3DES_EDE_CBC_SHA",
    0x90:"TLS_DHE_PSK_WITH_AES_128_CBC_SHA",
    0x91:"TLS_DHE_PSK_WITH_AES_256_CBC_SHA",
    0x92:"TLS_RSA_PSK_WITH_RC4_128_SHA",
    0x93:"TLS_RSA_PSK_WITH_3DES_EDE_CBC_SHA",
    0x94:"TLS_RSA_PSK_WITH_AES_128_CBC_SHA",
    0x95:"TLS_RSA_PSK_WITH_AES_256_CBC_SHA",
    0x96:"TLS_RSA_WITH_SEED_CBC_SHA",
    0x97:"TLS_DH_DSS_WITH_SEED_CBC_SHA",
    0x98:"TLS_DH_RSA_WITH_SEED_CBC_SHA",
    0x99:"TLS_DHE_DSS_WITH_SEED_CBC_SHA",
    0x9a:"TLS_DHE_RSA_WITH_SEED_CBC_SHA",
    0x9b:"TLS_DH_anon_WITH_SEED_CBC_SHA",
    0x9c:"TLS_RSA_WITH_AES_128_GCM_SHA256",
    0x9d:"TLS_RSA_WITH_AES_256_GCM_SHA384",
    0x9e:"TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
    0x9f:"TLS_DHE_RSA_WITH_AES_256_GCM_SHA384",
    0xa0:"TLS_DH_RSA_WITH_AES_128_GCM_SHA256",
    0xa1:"TLS_DH_RSA_WITH_AES_256_GCM_SHA384",
    0xa2:"TLS_DHE_DSS_WITH_AES_128_GCM_SHA256",
    0xa3:"TLS_DHE_DSS_WITH_AES_256_GCM_SHA384",
    0xa4:"TLS_DH_DSS_WITH_AES_128_GCM_SHA256",
    0xa5:"TLS_DH_DSS_WITH_AES_256_GCM_SHA384",
    0xa6:"TLS_DH_anon_WITH_AES_128_GCM_SHA256",
    0xa7:"TLS_DH_anon_WITH_AES_256_GCM_SHA384",
    0xa8:"TLS_PSK_WITH_AES_128_GCM_SHA256",
    0xa9:"TLS_PSK_WITH_AES_256_GCM_SHA384",
    0xaa:"TLS_DHE_PSK_WITH_AES_128_GCM_SHA256",
    0xab:"TLS_DHE_PSK_WITH_AES_256_GCM_SHA384",
    0xac:"TLS_RSA_PSK_WITH_AES_128_GCM_SHA256",
    0xad:"TLS_RSA_PSK_WITH_AES_256_GCM_SHA384",
    0xae:"TLS_PSK_WITH_AES_128_CBC_SHA256",
    0xaf:"TLS_PSK_WITH_AES_256_CBC_SHA384",
    0xb0:"TLS_PSK_WITH_NULL_SHA256",
    0xb1:"TLS_PSK_WITH_NULL_SHA384",
    0xb2:"TLS_DHE_PSK_WITH_AES_128_CBC_SHA256",
    0xb3:"TLS_DHE_PSK_WITH_AES_256_CBC_SHA384",
    0xb4:"TLS_DHE_PSK_WITH_NULL_SHA256",
    0xb5:"TLS_DHE_PSK_WITH_NULL_SHA384",
    0xb6:"TLS_RSA_PSK_WITH_AES_128_CBC_SHA256",
    0xb7:"TLS_RSA_PSK_WITH_AES_256_CBC_SHA384",
    0xb8:"TLS_RSA_PSK_WITH_NULL_SHA256",
    0xb9:"TLS_RSA_PSK_WITH_NULL_SHA384",
    0xba:"TLS_RSA_WITH_CAMELLIA_128_CBC_SHA256",
    0xbb:"TLS_DH_DSS_WITH_CAMELLIA_128_CBC_SHA256",
    0xbc:"TLS_DH_RSA_WITH_CAMELLIA_128_CBC_SHA256",
    0xbd:"TLS_DHE_DSS_WITH_CAMELLIA_128_CBC_SHA256",
    0xbe:"TLS_DHE_RSA_WITH_CAMELLIA_128_CBC_SHA256",
    0xbf:"TLS_DH_anon_WITH_CAMELLIA_128_CBC_SHA256",
    0xc0:"TLS_RSA_WITH_CAMELLIA_256_CBC_SHA256",
    0xc1:"TLS_DH_DSS_WITH_CAMELLIA_256_CBC_SHA256",
    0xc2:"TLS_DH_RSA_WITH_CAMELLIA_256_CBC_SHA256",
    0xc3:"TLS_DHE_DSS_WITH_CAMELLIA_256_CBC_SHA256",
    0xc4:"TLS_DHE_RSA_WITH_CAMELLIA_256_CBC_SHA256",
    0xc5:"TLS_DH_anon_WITH_CAMELLIA_256_CBC_SHA256",
    0xc6:"TLS_SM4_GCM_SM3",
    0xc7:"TLS_SM4_CCM_SM3",
    0xff:"TLS_EMPTY_RENEGOTIATION_INFO_SCSV",
    0x5600:"TLS_EMPTY_RENEGOTIATION_INFO_SCSV",
    0x1301:"TLS_AES_128_GCM_SHA256",
    0x1302:"TLS_AES_256_GCM_SHA384",
    0x1303:"TLS_CHACHA20_POLY1305_SHA256",
    0x1304:"TLS_AES_128_CCM_SHA256",
    0x1305:"TLS_AES_128_CCM_8_SHA256",
    0xc001:"TLS_ECDH_ECDSA_WITH_NULL_SHA",
    0xc002:"TLS_ECDH_ECDSA_WITH_RC4_128_SHA",
    0xc003:"TLS_ECDH_ECDSA_WITH_3DES_EDE_CBC_SHA",
    0xc004:"TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA",
    0xc005:"TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA",
    0xc006:"TLS_ECDHE_ECDSA_WITH_NULL_SHA",
    0xc007:"TLS_ECDHE_ECDSA_WITH_RC4_128_SHA",
    0xc008:"TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA",
    0xc009:"TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
    0xc00a:"TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
    0xc00b:"TLS_ECDH_RSA_WITH_NULL_SHA",
    0xc00c:"TLS_ECDH_RSA_WITH_RC4_128_SHA",
    0xc00d:"TLS_ECDH_RSA_WITH_3DES_EDE_CBC_SHA",
    0xc00e:"TLS_ECDH_RSA_WITH_AES_128_CBC_SHA",
    0xc00f:"TLS_ECDH_RSA_WITH_AES_256_CBC_SHA",
    0xc010:"TLS_ECDHE_RSA_WITH_NULL_SHA",
    0xc011:"TLS_ECDHE_RSA_WITH_RC4_128_SHA",
    0xc012:"TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA",
    0xc013:"TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
    0xc014:"TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
    0xc015:"TLS_ECDH_anon_WITH_NULL_SHA",
    0xc016:"TLS_ECDH_anon_WITH_RC4_128_SHA",
    0xc017:"TLS_ECDH_anon_WITH_3DES_EDE_CBC_SHA",
    0xc018:"TLS_ECDH_anon_WITH_AES_128_CBC_SHA",
    0xc019:"TLS_ECDH_anon_WITH_AES_256_CBC_SHA",
    0xc01a:"TLS_SRP_SHA_WITH_3DES_EDE_CBC_SHA",
    0xc01b:"TLS_SRP_SHA_RSA_WITH_3DES_EDE_CBC_SHA",
    0xc01c:"TLS_SRP_SHA_DSS_WITH_3DES_EDE_CBC_SHA",
    0xc01d:"TLS_SRP_SHA_WITH_AES_128_CBC_SHA",
    0xc01e:"TLS_SRP_SHA_RSA_WITH_AES_128_CBC_SHA",
    0xc01f:"TLS_SRP_SHA_DSS_WITH_AES_128_CBC_SHA",
    0xc020:"TLS_SRP_SHA_WITH_AES_256_CBC_SHA",
    0xc021:"TLS_SRP_SHA_RSA_WITH_AES_256_CBC_SHA",
    0xc022:"TLS_SRP_SHA_DSS_WITH_AES_256_CBC_SHA",
    0xc023:"TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256",
    0xc024:"TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384",
    0xc025:"TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA256",
    0xc026:"TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA384",
    0xc027:"TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
    0xc028:"TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
    0xc029:"TLS_ECDH_RSA_WITH_AES_128_CBC_SHA256",
    0xc02a:"TLS_ECDH_RSA_WITH_AES_256_CBC_SHA384",
    0xc02b:"TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    0xc02c:"TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    0xc02d:"TLS_ECDH_ECDSA_WITH_AES_128_GCM_SHA256",
    0xc02e:"TLS_ECDH_ECDSA_WITH_AES_256_GCM_SHA384",
    0xc02f:"TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    0xc030:"TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    0xc031:"TLS_ECDH_RSA_WITH_AES_128_GCM_SHA256",
    0xc032:"TLS_ECDH_RSA_WITH_AES_256_GCM_SHA384",
    0xc033:"TLS_ECDHE_PSK_WITH_RC4_128_SHA",
    0xc034:"TLS_ECDHE_PSK_WITH_3DES_EDE_CBC_SHA",
    0xc035:"TLS_ECDHE_PSK_WITH_AES_128_CBC_SHA",
    0xc036:"TLS_ECDHE_PSK_WITH_AES_256_CBC_SHA",
    0xc037:"TLS_ECDHE_PSK_WITH_AES_128_CBC_SHA256",
    0xc038:"TLS_ECDHE_PSK_WITH_AES_256_CBC_SHA384",
    0xc039:"TLS_ECDHE_PSK_WITH_NULL_SHA",
    0xc03A:"TLS_ECDHE_PSK_WITH_NULL_SHA256",
    0xc03B:"TLS_ECDHE_PSK_WITH_NULL_SHA384",
    0xc03C:"TLS_RSA_WITH_ARIA_128_CBC_SHA256",
    0xc03D:"TLS_RSA_WITH_ARIA_256_CBC_SHA384",
    0xc03E:"TLS_DH_DSS_WITH_ARIA_128_CBC_SHA256",
    0xc03F:"TLS_DH_DSS_WITH_ARIA_256_CBC_SHA384",
    0xc040:"TLS_DH_RSA_WITH_ARIA_128_CBC_SHA256",
    0xc041:"TLS_DH_RSA_WITH_ARIA_256_CBC_SHA384",
    0xc042:"TLS_DHE_DSS_WITH_ARIA_128_CBC_SHA256",
    0xc043:"TLS_DHE_DSS_WITH_ARIA_256_CBC_SHA384",
    0xc044:"TLS_DHE_RSA_WITH_ARIA_128_CBC_SHA256",
    0xc045:"TLS_DHE_RSA_WITH_ARIA_256_CBC_SHA384",
    0xc046:"TLS_DH_anon_WITH_ARIA_128_CBC_SHA256",
    0xc047:"TLS_DH_anon_WITH_ARIA_256_CBC_SHA384",
    0xc048:"TLS_ECDHE_ECDSA_WITH_ARIA_128_CBC_SHA256",
    0xc049:"TLS_ECDHE_ECDSA_WITH_ARIA_256_CBC_SHA384",
    0xc04A:"TLS_ECDH_ECDSA_WITH_ARIA_128_CBC_SHA256",
    0xc04B:"TLS_ECDH_ECDSA_WITH_ARIA_256_CBC_SHA384",
    0xc04C:"TLS_ECDHE_RSA_WITH_ARIA_128_CBC_SHA256",
    0xc04D:"TLS_ECDHE_RSA_WITH_ARIA_256_CBC_SHA384",
    0xc04E:"TLS_ECDH_RSA_WITH_ARIA_128_CBC_SHA256",
    0xc04F:"TLS_ECDH_RSA_WITH_ARIA_256_CBC_SHA384",
    0xc050:"TLS_RSA_WITH_ARIA_128_GCM_SHA256",
    0xc051:"TLS_RSA_WITH_ARIA_256_GCM_SHA384",
    0xc052:"TLS_DHE_RSA_WITH_ARIA_128_GCM_SHA256",
    0xc053:"TLS_DHE_RSA_WITH_ARIA_256_GCM_SHA384",
    0xc054:"TLS_DH_RSA_WITH_ARIA_128_GCM_SHA256",
    0xc055:"TLS_DH_RSA_WITH_ARIA_256_GCM_SHA384",
    0xc056:"TLS_DHE_DSS_WITH_ARIA_128_GCM_SHA256",
    0xc057:"TLS_DHE_DSS_WITH_ARIA_256_GCM_SHA384",
    0xc058:"TLS_DH_DSS_WITH_ARIA_128_GCM_SHA256",
    0xc059:"TLS_DH_DSS_WITH_ARIA_256_GCM_SHA384",
    0xc05A:"TLS_DH_anon_WITH_ARIA_128_GCM_SHA256",
    0xc05B:"TLS_DH_anon_WITH_ARIA_256_GCM_SHA384",
    0xc05C:"TLS_ECDHE_ECDSA_WITH_ARIA_128_GCM_SHA256",
    0xc05D:"TLS_ECDHE_ECDSA_WITH_ARIA_256_GCM_SHA384",
    0xc05E:"TLS_ECDH_ECDSA_WITH_ARIA_128_GCM_SHA256",
    0xc05F:"TLS_ECDH_ECDSA_WITH_ARIA_256_GCM_SHA384",
    0xc060:"TLS_ECDHE_RSA_WITH_ARIA_128_GCM_SHA256",
    0xc061:"TLS_ECDHE_RSA_WITH_ARIA_256_GCM_SHA384",
    0xc062:"TLS_ECDH_RSA_WITH_ARIA_128_GCM_SHA256",
    0xc063:"TLS_ECDH_RSA_WITH_ARIA_256_GCM_SHA384",
    0xc064:"TLS_PSK_WITH_ARIA_128_CBC_SHA256",
    0xc065:"TLS_PSK_WITH_ARIA_256_CBC_SHA384",
    0xc066:"TLS_DHE_PSK_WITH_ARIA_128_CBC_SHA256",
    0xc067:"TLS_DHE_PSK_WITH_ARIA_256_CBC_SHA384",
    0xc068:"TLS_RSA_PSK_WITH_ARIA_128_CBC_SHA256",
    0xc069:"TLS_RSA_PSK_WITH_ARIA_256_CBC_SHA384",
    0xc06A:"TLS_PSK_WITH_ARIA_128_GCM_SHA256",
    0xc06B:"TLS_PSK_WITH_ARIA_256_GCM_SHA384",
    0xc06C:"TLS_DHE_PSK_WITH_ARIA_128_GCM_SHA256",
    0xc06D:"TLS_DHE_PSK_WITH_ARIA_256_GCM_SHA384",
    0xc06E:"TLS_RSA_PSK_WITH_ARIA_128_GCM_SHA256",
    0xc06F:"TLS_RSA_PSK_WITH_ARIA_256_GCM_SHA384",
    0xc070:"TLS_ECDHE_PSK_WITH_ARIA_128_CBC_SHA256",
    0xc071:"TLS_ECDHE_PSK_WITH_ARIA_256_CBC_SHA384",
    0xc072:"TLS_ECDHE_ECDSA_WITH_CAMELLIA_128_CBC_SHA256",
    0xc073:"TLS_ECDHE_ECDSA_WITH_CAMELLIA_256_CBC_SHA384",
    0xc074:"TLS_ECDH_ECDSA_WITH_CAMELLIA_128_CBC_SHA256",
    0xc075:"TLS_ECDH_ECDSA_WITH_CAMELLIA_256_CBC_SHA384",
    0xc076:"TLS_ECDHE_RSA_WITH_CAMELLIA_128_CBC_SHA256",
    0xc077:"TLS_ECDHE_RSA_WITH_CAMELLIA_256_CBC_SHA384",
    0xc078:"TLS_ECDH_RSA_WITH_CAMELLIA_128_CBC_SHA256",
    0xc079:"TLS_ECDH_RSA_WITH_CAMELLIA_256_CBC_SHA384",
    0xc07A:"TLS_RSA_WITH_CAMELLIA_128_GCM_SHA256",
    0xc07B:"TLS_RSA_WITH_CAMELLIA_256_GCM_SHA384",
    0xc07C:"TLS_DHE_RSA_WITH_CAMELLIA_128_GCM_SHA256",
    0xc07D:"TLS_DHE_RSA_WITH_CAMELLIA_256_GCM_SHA384",
    0xc07E:"TLS_DH_RSA_WITH_CAMELLIA_128_GCM_SHA256",
    0xc07F:"TLS_DH_RSA_WITH_CAMELLIA_256_GCM_SHA384",
    0xc080:"TLS_DHE_DSS_WITH_CAMELLIA_128_GCM_SHA256",
    0xc081:"TLS_DHE_DSS_WITH_CAMELLIA_256_GCM_SHA384",
    0xc082:"TLS_DH_DSS_WITH_CAMELLIA_128_GCM_SHA256",
    0xc083:"TLS_DH_DSS_WITH_CAMELLIA_256_GCM_SHA384",
    0xc084:"TLS_DH_anon_WITH_CAMELLIA_128_GCM_SHA256",
    0xc085:"TLS_DH_anon_WITH_CAMELLIA_256_GCM_SHA384",
    0xc086:"TLS_ECDHE_ECDSA_WITH_CAMELLIA_128_GCM_SHA256",
    0xc087:"TLS_ECDHE_ECDSA_WITH_CAMELLIA_256_GCM_SHA384",
    0xc088:"TLS_ECDH_ECDSA_WITH_CAMELLIA_128_GCM_SHA256",
    0xc089:"TLS_ECDH_ECDSA_WITH_CAMELLIA_256_GCM_SHA384",
    0xc08A:"TLS_ECDHE_RSA_WITH_CAMELLIA_128_GCM_SHA256",
    0xc08B:"TLS_ECDHE_RSA_WITH_CAMELLIA_256_GCM_SHA384",
    0xc08C:"TLS_ECDH_RSA_WITH_CAMELLIA_128_GCM_SHA256",
    0xc08D:"TLS_ECDH_RSA_WITH_CAMELLIA_256_GCM_SHA384",
    0xc08E:"TLS_PSK_WITH_CAMELLIA_128_GCM_SHA256",
    0xc08F:"TLS_PSK_WITH_CAMELLIA_256_GCM_SHA384",
    0xc090:"TLS_DHE_PSK_WITH_CAMELLIA_128_GCM_SHA256",
    0xc091:"TLS_DHE_PSK_WITH_CAMELLIA_256_GCM_SHA384",
    0xc092:"TLS_RSA_PSK_WITH_CAMELLIA_128_GCM_SHA256",
    0xc093:"TLS_RSA_PSK_WITH_CAMELLIA_256_GCM_SHA384",
    0xc094:"TLS_PSK_WITH_CAMELLIA_128_CBC_SHA256",
    0xc095:"TLS_PSK_WITH_CAMELLIA_256_CBC_SHA384",
    0xc096:"TLS_DHE_PSK_WITH_CAMELLIA_128_CBC_SHA256",
    0xc097:"TLS_DHE_PSK_WITH_CAMELLIA_256_CBC_SHA384",
    0xc098:"TLS_RSA_PSK_WITH_CAMELLIA_128_CBC_SHA256",
    0xc099:"TLS_RSA_PSK_WITH_CAMELLIA_256_CBC_SHA384",
    0xc09A:"TLS_ECDHE_PSK_WITH_CAMELLIA_128_CBC_SHA256",
    0xc09B:"TLS_ECDHE_PSK_WITH_CAMELLIA_256_CBC_SHA384",
    0xc09c:"TLS_RSA_WITH_AES_128_CCM",
    0xc09d:"TLS_RSA_WITH_AES_256_CCM",
    0xc09e:"TLS_DHE_RSA_WITH_AES_128_CCM",
    0xc09f:"TLS_DHE_RSA_WITH_AES_256_CCM",
    0xc0a0:"TLS_RSA_WITH_AES_128_CCM_8",
    0xc0a1:"TLS_RSA_WITH_AES_256_CCM_8",
    0xc0a2:"TLS_DHE_RSA_WITH_AES_128_CCM_8",
    0xc0a3:"TLS_DHE_RSA_WITH_AES_256_CCM_8",
    0xc0a4:"TLS_PSK_WITH_AES_128_CCM",
    0xc0a5:"TLS_PSK_WITH_AES_256_CCM",
    0xc0a6:"TLS_DHE_PSK_WITH_AES_128_CCM",
    0xc0a7:"TLS_DHE_PSK_WITH_AES_256_CCM",
    0xc0a8:"TLS_PSK_WITH_AES_128_CCM_8",
    0xc0a9:"TLS_PSK_WITH_AES_256_CCM_8",
    0xc0aa:"TLS_PSK_DHE_WITH_AES_128_CCM_8",
    0xc0ab:"TLS_PSK_DHE_WITH_AES_256_CCM_8",
    0xc0ac:"TLS_ECDHE_ECDSA_WITH_AES_128_CC",
    0xc0ad:"TLS_ECDHE_ECDSA_WITH_AES_256_CCM",
    0xc0ae:"TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8",
    0xc0af:"TLS_ECDHE_ECDSA_WITH_AES_256_CCM_8",
    0xcc13:"TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256_OL",
    0xcc14:"TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256_OL",
    0xcc15:"TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256_OL",
    0xcca8:"TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA25",
    0xcca9:"TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA25",
    0xccaa:"TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA25",
    0xccab:"TLS_PSK_WITH_CHACHA20_POLY1305_SHA25",
    0xccac:"TLS_ECDHE_PSK_WITH_CHACHA20_POLY1305_SHA25",
    0xccad:"TLS_DHE_PSK_WITH_CHACHA20_POLY1305_SHA25",
    0xccae:"TLS_RSA_PSK_WITH_CHACHA20_POLY1305_SHA25",
    0xff00:"TLS_GOSTR341094_RSA_WITH_28147_CNT_MD",
    0xff01:"TLS_RSA_WITH_28147_CNT_GOST9",
    0xff02:"na",
    0xff03:"na",
    0xfefe:"SSL_RSA_FIPS_WITH_DES_CBC_SH",
    0xfeff:"SSL_RSA_FIPS_WITH_3DES_EDE_CBC_SH",
    0xfee0:"SSL_RSA_FIPS_WITH_3DES_EDE_CBC_SH",
    0xfee1:"SSL_RSA_FIPS_WITH_DES_CBC_SH",
    0x010080:"SSL_CK_RC4_128_WITH_MD5",
    0x020080:"SSL_CK_RC4_128_EXPORT40_WITH_MD5",
    0x030080:"SSL_CK_RC2_128_CBC_WITH_MD5",
    0x040080:"SSL_CK_RC2_128_CBC_EXPORT40_WITH_MD",
    0x050080:"SSL_CK_IDEA_128_CBC_WITH_MD5",
    0x060040:"SSL_CK_DES_64_CBC_WITH_MD5",
    0x060140:"SSL_CK_DES_64_CBC_WITH_SHA",
    0x0700c0:"SSL_CK_DES_192_EDE3_CBC_WITH_MD5",
    0x0701c0:"SSL_CK_DES_192_EDE3_CBC_WITH_SHA",
    0x080080:"SSL_CK_RC4_64_WITH_MD5",
    0xff0800:"SSL_CK_DES_64_CFB64_WITH_MD5_1",
    0xff0810:"SSL_CK_NULL"
}

    
extensions = {
    0:"server_name",
    1:"max_fragment_length",
    2:"client_certificate_url",
    3:"trusted_ca_keys",
    4:"truncated_hmac",
    5:"status_request",
    6:"user_mapping",
    7:"client_authz",
    8:"server_authz",
    9:"cert_type",
    10:"supported_groups",
    11:"ec_point_formats",
    12:"srp",
    13:"signature_algorithms",
    14:"use_srtp",
    15:"heartbeat",
    16:"application_layer_protocol_negotiation",
    17:"status_request_v2",
    18:"signed_certificate_timestamp",
    19:"client_certificate_type",
    20:"server_certificate_type",
    21:"padding",
    22:"encrypt_then_mac",
    23:"extended_master_secret",
    24:"token_binding",
    25:"cached_info",
    26:"tls_lts",
    27:"compress_certificate",
    28:"record_size_limit",
    29:"pwd_protect",
    30:"pwd_clear",
    31:"password_salt",
    32:"ticket_pinning",
    33:"tls_cert_with_extern_psk",
    34:"delegated_credentials",
    35:"session_ticket",
    36:"TLMSP",
    37:"TLMSP_proxying",
    38:"TLMSP_delegate",
    39:"supported_ekt_ciphers",
    40:"Reserved",
    41:"pre_shared_key",
    42:"early_data",
    43:"supported_versions",
    44:"cookie",
    45:"psk_key_exchange_modes",
    46:"Reserved",
    47:"certificate_authorities",
    48:"oid_filters",
    49:"post_handshake_auth",
    50:"signature_algorithms_cert",
    51:"key_share",
    52:"transparency_info",
    53:"connection_id (deprecated)",
    54:"connection_id",
    55:"external_id_hash",
    56:"external_session_id",
    57:"quic_transport_parameters",
    58:"ticket_request",
    59:"dnssec_chain",
    17513:"application_settings",
    65281:"renegotiation_info"
}

groups = {
    1:"sect163k1",
    2:"sect163r1",
    3:"sect163r2",
    4:"sect193r1",
    5:"sect193r2",
    6:"sect233k1",
    7:"sect233r1",
    8:"sect239k1",
    9:"sect283k1",
    10:"sect283r1",
    11:"sect409k1",
    12:"sect409r1",
    13:"sect571k1",
    14:"sect571r1",
    15:"secp160k1",
    16:"secp160r1",
    17:"secp160r2",
    18:"secp192k1",
    19:"secp192r1",
    20:"secp224k1",
    21:"secp224r1",
    22:"secp256k1",
    23:"secp256r1",
    24:"secp384r1",
    25:"secp521r1",
    26:"brainpoolP256r1",
    27:"brainpoolP384r1",
    28:"brainpoolP512r1",
    29:"x25519",
    30:"x448",
    31:"brainpoolP256r1tls13",
    32:"brainpoolP384r1tls13",
    33:"brainpoolP512r1tls13",
    34:"GC256A",
    35:"GC256B",
    36:"GC256C",
    37:"GC256D",
    38:"GC512A",
    39:"GC512B",
    40:"GC512C",
    41:"curveSM2",
    256:"ffdhe2048",
    257:"ffdhe3072",
    258:"ffdhe4096",
    259:"ffdhe6144",
    260:"ffdhe8192",
    65281:"arbitrary_explicit_prime_curves",
    65282:"arbitrary_explicit_char2_curves"
}

formats = {
    0:"uncompressed",
    1:"ansiX962_compressed_prime",
    2:"ansiX962_compressed_char2"
}


