	# -*- coding: UTF-8 -*-
# Port of the Mathematica Notebook.

from os import system
from functions import *
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk import FreqDist
from nltk.corpus import stopwords
import graduharvest
import numpy as np
import gensim

gradut_all = graduharvest.harvest(False, max = 3)
gradut = []
for g in gradut_all:
   print([k for k in g.abstracts.keys()])
   if "en" in g.abstracts.keys():
      #g.abstract = g.abstracts["en"]
      gradut.append(g)
   else:
      # translate here
      pass

print("Looking at ", len(gradut), "theses")

#this is redoing countWords but for abstracts
stop_words = set(stopwords.words("english"))
stemmer = SnowballStemmer("english", ignore_stopwords=True)
lemmatizer = WordNetLemmatizer()
for g in gradut:
   print(g.title)
   tokens = [word for word in word_tokenize(g.abstracts['en']) if word.isalpha() and word not in stop_words]
   # print(tokens[:10])

   # stems = [stemmer.stem(t) for t in tokens]
   lemmas = [lemmatizer.lemmatize(t) for t in tokens]
   freqdist = FreqDist(lemmas)
   print(freqdist.most_common(20))
   print(freqdist)
   g.freqdist = freqdist
   g.commonwords = [k for (k,n) in freqdist.most_common(20)]
   g.wordcount = len(freqdist)

#matrix
closenessMatrix = np.zeros((len(gradut),len(gradut)))
for i,g1 in enumerate(gradut):
   for g2 in gradut[i+1:]:
      pass
