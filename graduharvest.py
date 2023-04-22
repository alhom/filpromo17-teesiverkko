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

opparit_kaikki = 'com_10138_17738'
gradut_kaikki = 'com_10138_18086'
gradut_kaikki_2 = 'com_10138_23727'
vaikkarit_kaikki = 'com_10138_18060'
vaikkarit_kaikki_2 = 'com_10138_23720'
vaikkarit_kaikki_3 = 'col_10138_100'
vaikkarit_vanhat_laakis = 'col_10138_2251'
# Open the connection

# reharvest:
# -1 - use the large dump, needs filtering after
# 0 - only unpickle
# 1 - unpickle and reprocesss their metadata
# 2 - harvest again from HELDA, but only nonexisting entries
# 3 - harvest again from HELDA, everything
def harvest(reharvest = 0, max = 3):

   if reharvest == -1:
      gradut = loadTheses(False, filename="thesisdump_all.pkl")
   elif reharvest == 0:
      gradut = loadTheses(False)
   elif reharvest == 1:
      gradut = (loadTheses(True, filename=gradut_kaikki+".pkl") +
                loadTheses(True, filename=vaikkarit_kaikki+".pkl"))
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

#this is stupid
def getiidees(fromdate='2014-09-14', out="newiidees.txt"):
   sic = Sickle('http://helda.helsinki.fi/oai/request')
   with open(out,"a") as f:
      ids = sic.ListIdentifiers(**{'metadataPrefix':'oai_dc', 'set':vaikkarit_kaikki, 'from':fromdate})
      ii = ids.next()
      while ii:
         f.write(ii.identifier+'\n')
         print(ii.identifier)
         time.sleep(1)
         ii = ids.next()
      ids = sic.ListIdentifiers(**{'metadataPrefix':'oai_dc', 'set':gradut_kaikki, 'from':fromdate})
      ii = ids.next()
      while ii:
         f.write(ii.identifier+'\n')
         print(ii.identifier)
         time.sleep(1)
         ii = ids.next()

def main():
    getRecords(gradut_kaikki, max=1e32)
    
if __name__ == '__main__':
    main()