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


# List the records with the given key
reharvest = False
if reharvest:
	print('Harvesting theses')
	gradut = getGradus(matlu_gradut_1)
else:
	print('Loading theses')
	gradut = loadTheses()


for gradu in gradut:
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
