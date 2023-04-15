	# -*- coding: utf-8 -*-
from os import system
from functions import *

system('clear')


# Keys for different categories
matlu_gradut_1 = 'hdl_10138_18093'
matlu_gradut_2 = 'hdl_10138_36509'
matlu_lisurit = 'hdl_10138_18082'
matlu_vaikkarit = 'hdl_10138_18070'
matlu_vaikkarit_2 = 'hdl_10138_18141'
kayttis = 'hdl_10138_18094'

# Open the connection

# reharvest:
# 0 - only unpickle
# 1 - unpickle and reprocesss their metadata
# 2 - harvest again from HELDA, but only nonexisting entries
# 3 - harvest again from HELDA, everything
def harvest(reharvest = 2, max = 3):

   if reharvest == 0:
      gradut = loadTheses(False)
   elif reharvest == 1:
      gradut = loadTheses(True)
   elif reharvest == 2:
      print('Harvesting theses')
      gradut = loadTheses(False)
      gradut = getGradus(matlu_gradut_1, max=max, gradut = gradut)
   elif reharvest == 3:
      print('Harvesting theses')
      gradut = getGradus(matlu_gradut_1, max=max)
   # else:
   #    print('Loading theses')
   #    gradut = loadTheses()


   for gradu in gradut:
      pass
      #print(gradu.author+':\t\t'+gradu.title)
      print(gradu.unit)
      
      #print gradu.abstract
      if False:#'Alho' in gradu.author: #or 'Saressalo' in gradu.author:
         print(gradu.link)
         pdfname = downloadpdf(gradu.link)
         print(pdfname)
         countWords(gradu,pdfname)
         print(gradu)
         print('Keywords:')
         print(gradu.keywords)
         #system('rm '+pdfname[:-3]+'*')
   return gradut
