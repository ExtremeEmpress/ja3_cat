# Scripts folder structure

This folder contains the necessary scripts.

## data_converter.rb

Ruby script which exports data from the db.json file into separate files usable by the other scripts.

## generic_tester.py

Prints out the categorizations that the current best K-Means and LDA models give for the applications in the current source material.

## graphs.py

Script for drawing graphs.

## ja3_converter.py

Performs various conversions and tasks, such as returning mappings between JA3 pre-hash strings and applications in the current source material.

## ja3_distance.py

Implementation for calculating the distance between two JA3 pre-hash strings. Uses levenshtein distance.

## kmeans_model_finder.py

Runs K-Means on the source material for different topic sizes, and stores the model which gives best results.

## kmeans.py

Implementation for K-Means.

## lda_ja3.py

Implementation for LDA.

## lda_model_finder.py

Runs LDA on the source material for different topic sizes, and stores the model which gives best results.

## levenshtein.py

Implementation for Levenshtein distance for JA3's.

## which_app.py

Takes a JA3 pre-hash string as input, and returns a list of applications which have been categorized under the same topic in the current LDA model.
