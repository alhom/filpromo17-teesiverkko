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
         string = self.thesistype+' '
         if self.author: string += self.author+'\n'
         if self.weird != '': string += 'Weirdness found:\t\t'+self.weird+'\n'
         if self.title: string += 'Title:\t\t'+self.title+'\n'
         if self.unit: string += 'Unit:\t\t'+self.unit+'\n'
         if self.facultyid: string += 'facultyId:\t\t'+self.facultyid+'\n'
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
         string+='\n'

         return string
    
    def __init__(self, metadata=None):
      # Initializing the values
      self.metadata = {'identifier':'Missing'}
      self.id = '' # Helda ID
      self.langid = {}
      self.author = ''
      self.title = ''
      self.titles = {}
      self.abstract = ''
      self.abstracts = {}
      self.language = ''
      self.facultyid = 'other'
      self.faculty = ''
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
      self.weird = ''
      if metadata is not None:
          metaharvester(metadata, thesis=self)


def dumpTheses(gradut, filename='thesisdump.pkl'):
   gradut_dict = {g.id : g for g in gradut if hasattr(g,"id")}
   with open(filename,'wb') as output:
        	pickle.dump(list(gradut_dict.values()), output, pickle.HIGHEST_PROTOCOL)
                
def loadTheses(reprocess = False, filename='thesisdump.pkl', verbose=False):
   with open(filename,'rb') as inp:
      gradut = pickle.load(inp)
      print('Loaded %d theses' % len(gradut))
   if reprocess:
      print("Reprocessings")
      gradut_again = [metaharvester(g.metadata, verbose=verbose) for g in gradut if hasattr(g,"metadata")]
      return gradut_again
   else:
      return gradut

def filterTheses(gradut, indexfile="iideet_2023.txt"):
   gradut_dict = {g.id : g for g in gradut if hasattr(g, "id")}
   gradut = list(gradut_dict.values())
   if indexfile is not None:
      with open(indexfile,'r') as index:
         indexdata = index.read().splitlines()
         gradut_2 = [g for g in gradut if g.id in indexdata]
   return gradut_2


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
    readyids = [g.id for g in gradut]
    print(readyids)
    sickle = Sickle('http://helda.helsinki.fi/oai/request')
    with open('iideet_2023.txt','r') as f:
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
            if hasattr(g, "metadata"):
               g = metaharvester(metadata)
               if g is None:
                  continue
            else:
               continue
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

def getRecords(setname,fromdate='2014-09-14', untildate='2024-01-01', max = 3, dumpfile=None):

    # A function for reading the thesis entries from the database
    # fromdate as yyyy-mm-dd
    sickle = Sickle('http://helda.helsinki.fi/oai/request')
    recs = sickle.ListRecords(**{'metadataPrefix': 'oai_dc', 'set':setname, 'from':fromdate, 'until':untildate})
    nrecords = recs.oai_response.raw.count('</header>') # surely there is a better way of counting the records?
    print("Chunks of", nrecords, "available, of total", int(recs.resumption_token.complete_list_size))
    harvest = True
    gradut = []
    total = 0
    while harvest:
      ir = 0
      while ir < nrecords:
         try:
            record = recs.next()
         except:
             harvest = False
             break
         nrecords = recs.oai_response.raw.count('</header>')
         try:
            metadata = record.get_metadata()
         except:
            print("No metadata for record, skipping", record)
            continue

         g = metaharvester(metadata, verbose=False)
         if g is None:
            continue
         gradut.append(g)
         #print(metadata['description'][0])
         total = total+1
         if total >= max:
               print("Read max number of these thesis (max", max,")")
               break
         ir = ir+1
         print(total, ir, "/",nrecords)
         
      # get the next chunk if needed   
      if(total >= int(recs.resumption_token.complete_list_size)):
          harvest = False
          break
      else:
         print(total, "harvesting next batch")
         time.sleep(2.5)
         

   
    print('Found '+str(len(gradut))+' theses')
    if dumpfile==None:
      df = setname+".pkl"
    else:
      df = dumpfile
    dumpTheses(gradut, df)
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
                 "Artikelavhandling", "doctoralThesis", "Doctoral dissertation (article-based)", "Doctoral dissertation (monograph)",
                 ]
master_strs = ["pro gradu", "master's thesis"]

def metaharvester(metadata, thesis=None, verbose=True):
    # A function to read the metadatas obtained from ethesis and save them into Thesis objects

    if thesis is None:
      thisthesis = Thesis() # new Thesis object
    else:
      thisthesis = thesis

    thisthesis.metadata = metadata # Store the full metadata as well.
    try:
      thisthesis.id = [metadata['identifier'][i][22:] for i in range(len(metadata['identifier'])) if "hdl.handle" in metadata['identifier'][i]][0]
    except:
      return None


    # Try to find each metadata type, not all theses have all of these
    try: thisthesis.title = purify(str(metadata['title']))
    except: pass

    for abs in thisthesis.metadata['title']:
      # try:
         l = langdetect.detect(abs)
         if(verbose): print("adding title entry for ", l, ":", abs[:12],"...")
         thisthesis.titles[l] = abs
      # except:
      #    print("A weird title entry for ", metadata['title'], ":", abs[:12], "not using")

    try: thisthesis.author = purify(str(metadata['creator']))
    except: pass

    try:
        thisthesis.abstract = purify(str(metadata['description']))
        for abs in thisthesis.metadata['description']:
            try:
               l = langdetect.detect(abs)
               if(verbose): print("adding abstracts entry for ", l, ":", abs[:12],"...")
               thisthesis.abstracts[l] = abs
            except:
               print("A weird abstract entry for ", metadata['title'], ":", abs[:12], "not using")
    except:
        print("No abstract as 'description' for ", metadata['title'], metadata['identifier'], "trying title instead")
        try:
         thisthesis.abstract = purify(str(metadata['title']))
         for abs in thisthesis.metadata['title']:
               l = langdetect.detect(abs)
               if(verbose): print("adding abstracts entry for ", l, ":", abs[:12],"...")
               thisthesis.abstracts[l] = abs
         thisthesis.weird += 'No abstract. '
        except:
         print("Couldn't even use title! Empty string it is.") 
        

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
         brk = False
         if type == "Thesis" and any(["Finnish Meteorological Institute Contributions" in m for m in metadata['relation']]):
             thisthesis.thesistype = 'doctor'
             break
         for dtype in doctoral_strs:
          if dtype.casefold() in type.casefold():
              thisthesis.thesistype = 'doctor'
              brk = True
              break
         for dtype in master_strs:
          if dtype.casefold() in type.casefold():
              thisthesis.thesistype = 'master'
              brk = True
              break
         if brk:
             break
         
          
    except: pass
    # Faculty and department, omit the "University of Helsinki" in the beginning
    #  try: thisthesis.unit = purify(str(metadata['contributor']))[21:]
    #  except: pass
    try:
       thisthesis.unit = purify(str(metadata['contributor']))[21:]
       for abs in thisthesis.metadata['contributor']:
          if(verbose): print("adding unit entry,", abs[:12],"...")
          sabs = abs.split(", ")
          thisthesis.faculty = sabs[1]
          #thisthesis.unit[l] = abs[2]
          if "bio" in sabs[1].casefold():
              thisthesis.facultyid = "bio"
          if "matemaattis" in sabs[1].casefold():
              thisthesis.facultyid = "matlu"
          if "faculty of science" in sabs[1].casefold():
              thisthesis.facultyid = "matlu"
          if "humanistinen" in sabs[1].casefold():
              thisthesis.facultyid = "hum"
          if "arts" in sabs[1].casefold():
              thisthesis.facultyid = "hum"
          if "käyttäytymis" in sabs[1].casefold():
              thisthesis.facultyid = "cond"
          if "kasvatustie" in sabs[1].casefold():
              thisthesis.facultyid = "cond"
          if "social" in sabs[1].casefold(): #valtsikan relevantit ohjelmat condukseen?
              thisthesis.weird += "Strange faculty. "
              thisthesis.facultyid = "cond"
          if "educational" in sabs[1].casefold():
              thisthesis.facultyid = "cond"
          if "behavio" in sabs[1].casefold():
              thisthesis.facultyid = "cond"
          if "lääket" in sabs[1].casefold(): # Psykologit oli conduslaisia?
              thisthesis.weird += "Strange faculty. "
              thisthesis.facultyid = "cond"
          if "farmasian" in sabs[1].casefold():
              thisthesis.facultyid = "farm"
          if "pharmacy" in sabs[1].casefold():
              thisthesis.facultyid = "farm"
          if "maatalous" in sabs[1].casefold():
              thisthesis.weird += "Strange faculty. "
              thisthesis.facultyid = "bio"
          if "agriculture".casefold() in sabs[1].casefold():
              thisthesis.weird += "Strange faculty. "
              thisthesis.facultyid = "bio"
    except: pass
    if thisthesis.facultyid == "other":
      try:
       if any(["Meteorological"in m for m in metadata['relation']]):
         thisthesis.facultyid = "matlu"
      except:
          pass
      try:
       if any(["Ilmatieteen laitos" in m for m in metadata['publisher']]):
         thisthesis.facultyid = "matlu"
      except:
         pass
    

    # Make sure that the link is correct
    thisthesis.link = thisthesis.link[thisthesis.link.find('http'):]
    if(verbose): print(thisthesis)
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
