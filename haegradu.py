from sickle import Sickle
from time import sleep

setname = 'hdl_10138_18093' 
sickle = Sickle('http://helda.helsinki.fi/oai/request')

with open('iideet.txt','r') as f:
	for line in f:
		identifier = 'oai:helda.helsinki.fi:'+line.strip()
		record = sickle.GetRecord(**{'metadataPrefix': 'oai_dc','identifier': identifier})
		metadata = record.metadata
		print(metadata['description'][0])
		sleep(1)
		break
