	# -*- coding: UTF-8 -*-
from os import system
import lxml, urllib3 as urllib2
from sickle import Sickle
import time
import pickle
import ftfy
import langdetect

class Thesis(object):
    def __repr__(self):
        return "Thesis()"
    def __str__(self):
		# Function for printing the data of the thesis
         string = self.thesistype+':\n'
         if self.title: string += 'Title:\t\t'+self.title+'\n'
         if self.author: string += 'Author:\t\t'+self.author+'\n'
         if self.unit: string += 'Unit:\t\t'+self.unit+'\n'
         if self.subject: string += 'Subject:\t'+self.subject+'\n'
         if self.language: string += 'Language:\t'+self.language+'\n'
         if self.date: string += 'Date:\t\t'+self.date+'\n'
         if self.link: string += 'Link:\t\t'+self.link+'\n'
         if self.abstracts: string += 'Abs.languages:\t\t'+str(list(self.abstracts.keys()))+'\n'
         #if self.keywords: string += 'Keywords:\t'+self.keywords+'\n'
         if self.wordcount: string += 'Word count:\t'+str(self.wordcount)+'\n'
         if self.charcount: string += 'Char count:\t'+str(self.charcount)+'\n'
         if self.figurecount: string += 'Figure count:\t\t'+str(self.figurecount)+'\n'
         if self.pagecount: string += 'Page count:\t\t'+str(self.pagecount)+'\n'


         return string
    
    def __init__(self, metadata=None):
      # Initializing the values
      self.id = ''
      self.author = ''
      self.title = ''
      self.abstract = ''
      self.abstracts = {}
      self.language = ''
      self.unit = ''
      self.date = ''
      self.link = ''
      self.subject = ''
      self.thesistype = ''
      self.keywords = []
      self.commonwords = []
      self.wordcount = 0
      self.charcount = 0
      self.figurecount = 0
      self.pagecount = 0
      if metadata is not None:
          metaharvester(metadata, thesis=self)


def dumpTheses(gradut):
	with open('thesisdump.pkl','wb') as output:
        	pickle.dump(gradut, output, pickle.HIGHEST_PROTOCOL)
def loadTheses(reprocess = False):
   with open('thesisdump.pkl','rb') as inp:
            gradut = pickle.load(inp)
   print('Loaded %d theses' % len(gradut))
   if reprocess:
      print("Reprocessings")
      gradut_again = [metaharvester(g.metadata) for g in gradut]
      return gradut_again
   else:
      return gradut

def downloadpdf(url):
    # A function to download a pdf file from a link to http://ethesis.helsinki.fi/
    res = urllib2.urlopen(url)
    source = res.read()

    # Find the corresponding line
    start =  source.find('<meta content="https://helda.helsinki.fi/bitstream/')
    end = source.find('.pdf',start)
    pdfurl = source[start+15:end+4]
    pdfname = pdfurl.split('/')[-1] # extract the file name from the url
    
    if pdfurl != '':
        pdffile = open(pdfname,'w') # create a file with the name of the pdf
        res = urllib2.urlopen(pdfurl)
        pdffile.write(res.read()) # write the content of the pdf link into the pdf file on the computer
        pdffile.close()
    
    # the file is now saved on the computer, return the filename (=> path?)
    return pdfname

def getGradus(setname,fromdate='2014-09-14', max = 3, gradut = []):

    # A function for reading the thesis entries from the database
    # fromdate as yyyy-mm-dd

    # Check which ids we already have loaded. Ugly double comprehesion, since the identifiers are not sorted. 
    readyids = [g.metadata['identifier'][i][22:] for g in gradut for i in range(len(g.metadata['identifier'])) if "hdl.handle" in g.metadata['identifier'][i]]
    print(readyids)
    sickle = Sickle('http://helda.helsinki.fi/oai/request')
    with open('iideet.txt','r') as f:
        i = 0
        for line in f:
            identifier = 'oai:helda.helsinki.fi:'+line.strip()
            if line.strip() in readyids:
               print(identifier, "already read, skipping")
               i = i+1
               continue
            print("Querying HELDA for ", identifier)
            record = sickle.GetRecord(**{'metadataPrefix': 'oai_dc','identifier': identifier})
            try:
               metadata = record.get_metadata()
            except:
               print("No metadata for", line.strip(), "skipping record",record)
               continue

            g = metaharvester(metadata)
            if (g.id not in readyids):
               gradut.append(g)
            #print(metadata['description'][0])
            time.sleep(1)
            i = i+1
            if i >= max:
                print("Read max number of these thesis (max", max,")")
                break
    
#    while n > 0:
#        gradulist,n = recordharvester(command)
#        gradut += gradulist
#	print '%d records harvested, sleep a second' % n
        
    print('Found '+str(len(gradut))+' theses')
    dumpTheses(gradut)
    return gradut

#cases for entry strings: 
# ['str']
# [u'str'] (with string containing special characters (unicode flag?)
# ["str"] (with string containing ')
def purify(string):
   start = 2
   if string.startswith('[u'):
      start = 3
   stri = string[start:-2]
   #stri = ftfy.fix(stri)
   return stri

# def recordharvester(records):
#    # A function to read the metadatas obtained from ethesis and save them into Thesis objects 
#    theses = []
#    n = 0
#    while True:
#       # Look for the next thesis until there are no more
#       try: metadata = records.next().get_metadata()
#       except: break

#       n += 1
#       thisthesis = Thesis() # new Thesis object
      
#       # Try to find each metadata type, not all theses have all of these
#       try: thisthesis.title = purify(str(metadata['title']))
#       except: pass

#       try: thisthesis.author = purify(str(metadata['creator']))
#       except: pass

#       try: thisthesis.abstract = purify(str(metadata['description']))
#       except: pass

#       try: thisthesis.language = str(metadata['language'])[2:-2]
#       except: pass
#       try: thisthesis.date = str(metadata['date'])[2:-2]
#       except: pass
#       # Link to the ethesis page
#       try: thisthesis.link = str(metadata['identifier'])[2:-2]
#       except: pass
#       try: thisthesis.subject = str(metadata['subject'])[1:-1]
#       except: pass
#       # Master's or Doctoral
#       try: thisthesis.thesistype = purify(str(metadata['type']))
#       except:
#          print("Error for ",metadata['type'])
#          pass
#       # Faculty and department, omit the "University of Helsinki" in the beginning
#       try: thisthesis.unit = purify(str(metadata['contributor']))[21:]
#       except: pass
      
#       # Make sure that the link is correct
#       thisthesis.link = thisthesis.link[thisthesis.link.find('http'):] 
#       theses.append(thisthesis) # add the thesis to the theses array
#       print(thisthesis)
#       time.sleep(0.2)
    
#    return theses,n

doctoral_strs = ["doctoral", "väitöskirja", "Monografiavhandling", 
                 "Artikelavhandling", "doctoralThesis", "Doctoral dissertation (article-based)", "Doctoral dissertation (monograph)"]
master_strs = ["pro gradu", "master's thesis"]

def metaharvester(metadata, thesis=None):
    # A function to read the metadatas obtained from ethesis and save them into Thesis objects

    if thesis is None:
      thisthesis = Thesis() # new Thesis object
    else:
      thisthesis = thesis

    thisthesis.metadata = metadata # Store the full metadata as well.

    thisthesis.id = [metadata['identifier'][i][22:] for i in range(len(metadata['identifier'])) if "hdl.handle" in metadata['identifier'][i]][0]


    # Try to find each metadata type, not all theses have all of these
    try: thisthesis.title = purify(str(metadata['title']))
    except: pass

    try: thisthesis.author = purify(str(metadata['creator']))
    except: pass

    try:
        thisthesis.abstract = purify(str(metadata['description']))
        for abs in thisthesis.metadata['description']:
            l = langdetect.detect(abs)
            print("adding abstracts entry for ", l, ":", abs[:12],"...")
            thisthesis.abstracts[l] = abs
    except: pass

    try: thisthesis.language = str(metadata['language'])[2:-2]
    except: pass
    try: thisthesis.date = str(metadata['date'])[2:-2]
    except: pass
    # Link to the ethesis page
    try: thisthesis.link = str(metadata['identifier'])[2:-2]
    except: pass
    try: thisthesis.subject = str(metadata['subject'])[1:-1]
    except: pass
    # Master's or Doctoral - now collates to two tags: doctor/master
    try:
      thisthesis.thesistype = purify(str(metadata['type']))
      for type in metadata['type']:
         for dtype in doctoral_strs:
          if dtype.casefold() in type.casefold():
              thisthesis.thesistype = 'doctor'
              break
         for dtype in master_strs:
          if dtype.casefold() in type.casefold():
              thisthesis.thesistype = 'master'
              break
         
          
    except: pass
    # Faculty and department, omit the "University of Helsinki" in the beginning
    try: thisthesis.unit = purify(str(metadata['contributor']))[21:]
    except: pass

    # Make sure that the link is correct
    thisthesis.link = thisthesis.link[thisthesis.link.find('http'):]
    print(thisthesis)
    return thisthesis


def countWords(gradu,pdfname):
    # A function to count the number of words, characters and the most common words in a pdf
    fname = pdfname[:-3]+'txt' # a txt file to save the words
    words = {} # word dictionary
    tempword = ''
    wordcount = 0
    charcount = 0
    keywords = []
    keys = False # flag that shows if keywords were found
    
    # Using pdfminer (https://pypi.python.org/pypi/pdfminer/) to extract the words into the txt file
    system('python pdf2txt.py '+pdfname+' >> '+fname)
    
    # Reading the word list
    f = open(fname,'r')

    # The punctuation characters should not be counted as part of a word
    punctuations = ['.',',',':',';','?','!',"'",'"','”','»',"’",'-','–','—','−', \
    '(',')','[',']','{','}','〈','〉','<','>','...','/','\\' \
    '§','½','@','#','£','¤','$','%','&','=','+','*']
    linechars = ['-','–','—','−'] # characters used for hyphenation

    # Go through all the lines in the text
    for line in f:
    
        # Search for keywords
        if not keys:
            if 'Avainsanat' in line or 'Nyckelord' in line or 'Keywords' in line:
                keys = True # Keywords on the next line
        elif keys:
            # Kwyrods on this line
            for word in line.lower().split(','):
            # Save the keyword if it's a word
                if not word.strip() in keywords:
                    keywords.append(word.strip())
            keys = False
            
        # Check if a word continues from previous line
        if tempword != '':
            line = tempword+line
            tempword = ''
        
        # Split the line into words    
        linewords = line.split()
        
        # Go through each word
        for word in linewords:
        
        # Check if the word continues on the next line 
            if word[-1] in linechars and word == linewords[-1]:
                tempword = word[:-1]
                continue
            
        # Check if the word has punctuation marks in the beginning or end and remove such marks    
            if word in punctuations: continue # one character word consisting of punctuations
            if word[-1] in punctuations: word = word[:-1] # strip punctuation mark in the end of the word
            if word[0] in punctuations: word = word[1:] # strip punctuation mark in the beginning of the word

            word = word.lower() # Compare only lowercase words
            wordcount += 1
            charcount += len(word)
            
        # If the word is already in the word list, increase it's count, otherwise add a new word
            if word in words: words[word] += 1
            else: words[word] = 1
    
    f.close()
    
    # Sorting the word list, the most mentioned word goes to last one
    words = sorted(words.iteritems(), key=lambda k,v: (v,k))
    # Strip the counts of single words (from dictionary to word list)
    words = [w[0] for w in words]
    # Remove the common words
    words = stripcommon(words)
    
    # If no keywords found, take the 5 most common words as keywords
    if not keywords:
        keywords = words[-5:]
    
    gradu.commonwords = words[-20:] # save 20 most common words in the thesis
    gradu.wordcount = wordcount # save the wordcount
    gradu.charcount = charcount # save the character count
    gradu.keywords = keywords # save the keywords
    # gradu.pagecount = TBA
    
    return

def stripcommon(wordlist):
    # A function to get rid of too common words in the common words list, not yet fully implemented
    wordfile = open('wordlist_en.txt','r')
    commonwords = wordfile.readlines()
    commonwords = [word.strip() for word in commonwords]
    print(wordlist.index('the'))
    strippedlist = wordlist
    for word in wordlist:
        if word in commonwords:
            strippedlist.remove(word)
    
    return strippedlist
