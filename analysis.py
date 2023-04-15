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
import sys
import gensim
from gensim import corpora as gcorpora
from gensim import models
from gensim import similarities
import libvoikko
import lemmy
import matplotlib.pyplot as plt
import matplotlib

class dummyworder:
   def stem(token):
      return token
   def lemmatize(token):
      return token

class Voikotin:
   def __init__(self):
      self.v = libvoikko.Voikko(u'fi')

   def lemmatize(self, token):
      a = self.v.analyze(token)
      if (a):
         return a[0]['BASEFORM']
      else:
         return token

class Lemmytizer:
   def __init__(self):
      self.lemmy = lemmy.load('sv')
   def lemmatize(self, token):
      return self.lemmy.lemmatize("",token)[0]

gradut_all = graduharvest.harvest(reharvest=0, max = 1e32)
gradut = {}
abslangs = {}
singlelans = {}
# Collect theses by availabe abstract languages
for g in gradut_all:
   for k in g.abstracts.keys():
      try:
         gradut[k].append(g)
         abslangs[k] = abslangs[k]+1
      except:
         gradut[k] = [g]
         abslangs[k] = 1
   if(len(g.abstracts.keys())==1):
      l = list(g.abstracts.keys())[0]
      print(g.metadata['identifier'], 'has only single language abstract, ', l)
      try:
         singlelans[l] = singlelans[l]+1
      except:
         singlelans[l] = 1


print("Looking at ", len(gradut_all), "theses, statistics")
print("Abstract languages:")
for al in abslangs.keys():
   print("abstracts of language", al, abslangs[al])
print("Single language abstracts in languages", singlelans)

langs = ["en", "fi", "sv"]
print("Analysing following languages:", langs)

voikotin = Voikotin()
lemmytizer = Lemmytizer()

#this is redoing countWords but for abstracts
# ... also redoing it by just calling 
stemmers = {
   'en' : SnowballStemmer("english", ignore_stopwords=True),
   'fi' : SnowballStemmer("finnish", ignore_stopwords=True),
   'sv' : SnowballStemmer("swedish", ignore_stopwords=True)
   }
stop_wordss = {
   'en' : set(stopwords.words("english")),
   'fi' : set(stopwords.words("finnish")),
   'sv' : set(stopwords.words("swedish")),
   }
lemmatizers = {
   'en' : WordNetLemmatizer(),
   'fi' : voikotin,
   'sv' : lemmytizer
}

# Build initial corpora
corpora = {}
for lang in langs:
   corpora[lang] = {}
   try:
      stop_words = stop_wordss[lang]
   except:
      print("No stop words found for language", lang, "using no stopwords")
      stop_words = {}
   try:
      stemmer = stemmers[lang]
   except:
      print("No stemmer for language", lang)
      stemmer = dummyworder
   try:
      lemmatizer = lemmatizers[lang]
   except:
      print("No lemmatizer for language", lang)
      lemmatizer = dummyworder
   
   for g in gradut[lang]:
      # print(g.title)
      tokens = [word for word in word_tokenize(g.abstracts[lang]) if word.isalpha() and word not in stop_words]
      # print(tokens[:10])

      # stems = [stemmer.stem(t) for t in tokens]
      lemmas = [lemmatizer.lemmatize(t) for t in tokens]
      # freqdist = FreqDist(lemmas)
      # print(freqdist.most_common(5))
      # print(freqdist)
      # g.freqdist = freqdist
      # g.commonwords = [k for (k,n) in freqdist.most_common(20)]
      # g.wordcount = len(freqdist)
      corpora[lang][g.id] = lemmas

#handle the corpora with gensim

gdicts = {}
gbows = {}
gmodels = {}
gindices = {}
for lang in langs:
   print("Gensim:", lang)
   corpus = corpora[lang]
   gdicts[lang] = gcorpora.Dictionary(corpus.values())
   gbows[lang] = [gdicts[lang].doc2bow(text) for text in corpus.values()]
   print(gdicts[lang])
   gmodels[lang] = models.TfidfModel(gbows[lang])
   nf=len(gdicts[lang].dfs)
   gindices[lang] = similarities.SparseMatrixSimilarity(gbows[lang], num_features=nf)



# generate similarity matrices
similarities = {}

for lang in langs:
   print("similarity checking:", lang)

   corpus = corpora[lang]
   similarities[lang] = np.zeros((len(corpus),len(corpus)))
   index = gindices[lang]
   model = gmodels[lang]
   print(model, index)
   for i,query in enumerate(corpus):
      bow = gbows[lang][i]
      print("querying", list(corpora[lang].keys())[i])
      tfids = index[model[bow]]
      #print(tfids)
      similarities[lang][i,:] = np.array(tfids)

   
   fig = plt.figure()
   plt.matshow(similarities[lang], norm=matplotlib.colors.LogNorm(vmin=1e-2, vmax=1))
   plt.savefig("matrix_"+lang+".png")

