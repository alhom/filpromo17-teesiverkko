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
from gensim import similarities as gsimilarities
import libvoikko
import lemmy
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import langcodes

def langname(l):
   langcodes.Language.get(l).display_name().lower()

def fmt_abstracts(adict):
   retstr = ""
   for k,v in adict.items():
      retstr +=k +"\n" + v + "\n\n" #unfortunately the line breaks do nothing
   return retstr

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

facultycolors={ 
   'hum'  :np.array([ 87,112,194])/255,
   'matlu':np.array([228,169, 36])/255,
   'farm' :np.array([106,185,155])/255,
   'bio'  :np.array([126,190, 39])/255,
   'cond' :np.array([238,213, 39])/255,
   'other':np.array([242,241,236])/275 #isabelline but darker
}


gradut_alll = graduharvest.harvest(reharvest=0, max = 1e32)
print("gradut_alll len", len(gradut_alll))
gradut_all = filterTheses(gradut_alll)
print("gradut_alll len after filter", len(gradut_alll))
print("gradut_all len", len(gradut_all))

dumpTheses(gradut_all) # get the missing ones
gradut_missing = graduharvest.harvest(reharvest=2, max = 1e32)
gradut_all = gradut_missing
dumpTheses(gradut_all)
dumpTheses(gradut_alll+gradut_missing, "thesisdump_all.pkl")
#sys.exit()
gradut = {}
abslangs = {}
singlelans = {}
# Collect theses by availabe abstract languages

for i,g in enumerate(gradut_all):
   g.global_id = i
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
langs = [l for l in abslangs.keys() if abslangs[l] > 1]
print("Analysing following languages:", [langname(l) for l in langs])

voikotin = Voikotin()
lemmytizer = Lemmytizer()

#this is redoing countWords but for abstracts
# ... also redoing it by just calling 
stemmers = {
   # 'en' : SnowballStemmer("english", ignore_stopwords=True),
   # 'fi' : SnowballStemmer("finnish", ignore_stopwords=True),
   # 'sv' : SnowballStemmer("swedish", ignore_stopwords=True),
   # 'de' : SnowballStemmer("german", ignore_stopwords=True),
   }
for l in langs:
   try:
      stemmers[l] = SnowballStemmer(langname(l))
   except:
      stemmers[l] = dummyworder

stop_wordss = {
   # 'en' : set(stopwords.words("english")),
   # 'fi' : set(stopwords.words("finnish")),
   # 'sv' : set(stopwords.words("swedish")),
   }
for l in langs:
   try:
      stop_wordss[l] = set(stopwords.words(langname(l)))
   except:
      pass

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
      print("No lemmatizer for language, trying with stemmer", lang)
      try:
         lemmatizer = dummyworder #stemmers[lang]
      except:
         print("No stemmer for language", lang)
         lemmatizer = dummyworder
   
   for g in gradut[lang]:
      # print(g.title)
      tokens = [word for word in word_tokenize(g.abstracts[lang]) if word.isalpha() and word not in stop_words]
      if len(tokens) == 0:
         pass # not even proper keywords in metadata
      # print(tokens[:10])

      # stems = [stemmer.stem(t) for t in tokens]
      lemmas = [lemmatizer.lemmatize(t) for t in tokens]
      # freqdist = FreqDist(lemmas)
      # print(freqdist.most_common(5))
      # print(freqdist)
      # g.freqdist = freqdist
      # g.commonwords = [k for (k,n) in freqdist.most_common(20)]
      # g.wordcount = len(freqdist)
      corpora[lang][g.global_id] = lemmas

skipsims = False
try:
   with open("similarities.pkl",'rb') as input:
      similarities = pickle.load(input)
      skipsims = True
except:
   similarities = {}

#handle the corpora with gensim - no need if similarities matrices exist
if not skipsims:
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
      gindices[lang] = gsimilarities.SparseMatrixSimilarity(gbows[lang], num_features=nf)



# generate similarity matrices
if not skipsims:
 for lang in langs:
   print("similarity checking:", lang)

   corpus = corpora[lang]
   similarities[lang] = np.zeros((len(corpus),len(corpus)))
   index = gindices[lang]
   model = gmodels[lang]
   print(model, index)
   for i,query in enumerate(corpus):
      bow = gbows[lang][i]
      #print("querying", list(corpora[lang].keys())[i])
      tfids = index[model[bow]]
      #print(tfids)
      similarities[lang][i,:] = np.array(tfids)

   fig = plt.figure()
   plt.matshow(similarities[lang], norm=matplotlib.colors.LogNorm(vmin=1e-2, vmax=1))
   plt.savefig("matrix_"+lang+".png")

with open("similarities.pkl",'wb') as output:
      pickle.dump(similarities, output, pickle.HIGHEST_PROTOCOL)


similarities_all = np.zeros((len(gradut_all),len(gradut_all)))
contribution_counts = np.zeros((len(gradut_all),len(gradut_all)),dtype=np.int8)

nwords = np.zeros(len(gradut_all))
ncontribs = np.zeros(len(gradut_all))

# for i,g in enumerate(gradut_all):
for lang in langs:
   spread = np.array(list(corpora[lang].keys()),dtype=np.int64)
   #similarities_dummy = np.zeros((len(gradut_all),len(gradut_all)))

   for i, id in enumerate(corpora[lang].keys()):
      nwords[id] += len(corpora[lang][id])
      ncontribs[id] += 1
      for j, jd in enumerate(corpora[lang].keys()):
         # similarities_dummy[id,jd] = similarities[lang][i,j]
         similarities_all[id,jd] += similarities[lang][i,j]
         contribution_counts[id,jd] += 1
   # similarities_all[spread,:][:,spread] += similarities[lang]
   # contribution_counts[spread,:][:,spread] += 1
   # fig = plt.figure()
   # plt.matshow(similarities_dummy, norm=matplotlib.colors.LogNorm(vmin=1e-2, vmax=1))
   # plt.savefig("matrix_dummy_"+lang+".png")
   # similarities_all += similarities_dummy

np.divide(similarities_all, contribution_counts, out=similarities_all,where=contribution_counts>0)
np.divide(nwords, ncontribs, out=nwords,where=ncontribs>0)

with open("similarities_all.pkl",'wb') as output:
   pickle.dump(similarities_all, output, pickle.HIGHEST_PROTOCOL)

fig = plt.figure()
plt.matshow(similarities_all, norm=matplotlib.colors.LogNorm(vmin=1e-2, vmax=1))
plt.savefig("matrix_all.png")


fig = plt.figure()
plt.matshow(contribution_counts)
plt.savefig("matrix_contribs.png")

fig = plt.figure()
plt.plot(nwords)
plt.savefig("num_words.png")


# Time to start creating the graph, using networkx
edgesfromnode = 5
G = nx.Graph()

for p,g in enumerate(gradut_all):
   i = g.global_id
   G.add_node(i)
   G.nodes[i]["author"] = g.author
   G.nodes[i]["label"] = g.author
   G.nodes[i]["facultyid"] = g.facultyid
   G.nodes[i]["type"] = g.thesistype
   G.nodes[i]["faculty"] = g.faculty
   #G.nodes[i]["unit"] = g.unit
   G.nodes[i]["url"] = g.link
   G.nodes[i]["title"] = g.title
   G.nodes[i]["subject"] = g.subject

   # Keep this/these last, lots of text... but ofc it's not sorted
   G.nodes[i]["abstract"] = fmt_abstracts(g.abstracts)

   if(p == 0):
      print("skibidi")
      continue
   
   # print(similarities_all[i,:i])
   topsi = np.argsort(similarities_all[i,:]).flatten()[::-1]
   # print(topsi)
   wmax = similarities_all[i,topsi[1]]
   if(wmax == 0):
      G.remove_node(i)
      print("No connections for ", g, ", sad")
      continue
   # print(g.author, i, topsi[:5])
   for j in topsi[1:edgesfromnode]:
      if(j == i): continue
      if((similarities_all[i,j] == 0) or (similarities_all[i,j] < wmax*0.01)):
         break
      G.add_edge(i,j)
      G.edges[i,j]["weight"] = similarities_all[i,j]**2

   # for j,g2 in enumerate(gradut_all):
   #    if(j == i):
   #       break
   #    j = g2.global_id
      
   #    if(similarities_all[i,j] > 0.05):
   #       G.add_edge(i,j)
   #       G.edges[i,j]["weight"] = similarities_all[i,j]**20

#nx.write_graphml(G, "graph.graphml")
#straight to gexf after layout


beaublue = "#c5e1ff"
babypowder = "#fffefa"
isabelline = "#f2f1ec"
azure = "#3b89fe"
lgold = "#f9e79e"
offorange = "#e9bc76"
fig = plt.figure()
fig.tight_layout()
pos = nx.spring_layout(G, weight ="weight", seed=1969, iterations=100)  # nearly the same as Gephi Force

colors = [facultycolors[G.nodes[g]["facultyid"]] for g in G.nodes]
lwgts = np.array([G.edges[g]["weight"] for g in G.edges])**0.5

nodesize = {"doctor": 10, "master": 2}

options = {'node_size': [nodesize[G.nodes[g]["type"]] for g in G.nodes],
           'node_color':colors,
           'width':2*lwgts,
           'edge_color':lgold+"55",
           'labels':{g : G.nodes[g]["author"] for g in G.nodes},
           'font_size':1,
           'font_color':azure
           }

#pos = nx.kamada_kawai_layout(G, weight ="weight")  # a bit messy, but maybe fine
#pos = nx.spectral_layout(G, weight ="weight")  # actual cluster disappears...

nx.draw(G, pos, **options, ax=plt.gca())

plt.savefig("agraph.svg", facecolor=beaublue)

#the the gexf export. Need to put vis data to ["viz"]..
gexfscale = 100
nodesize = {"doctor": 0.1, "master": 0.05}
nodeshape = {"doctor":'square', 'master':'disc'}

for g in G.nodes:
   c = facultycolors[G.nodes[g]["facultyid"]]
   G.nodes[g]["viz"] = {'size'    : nodesize[G.nodes[g]["type"]],
                        'position': {'x':pos[g][0]*gexfscale, 'y':pos[g][1]*gexfscale,'z':0.0},
                        'color'   : {'r':int(c[0]*255),'g':int(255*c[1]),'b':int(255*c[2])},
                        'shape'   : nodeshape[G.nodes[g]["type"]]
                        }
for e in G.edges:
   G.edges[e]["viz"] = {'thickness': G.edges[e]["weight"]**0.5, #this does nothing?
                        }

nx.write_gexf(G,"html/graph.gexf")