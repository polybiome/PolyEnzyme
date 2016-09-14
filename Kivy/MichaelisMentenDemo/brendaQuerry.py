import string
import hashlib
from suds.client import Client #from SOAPpy import WSDL ## for extracting the URL of the endpoint (server script) from the WSDL file
from suds.xsd.doctor import Import, ImportDoctor
#from brenda import BRENDAParser
import logging
import random
def search(organism,ecnumber,Km_or_Ki):
	#imp = Import('http://schemas.xmlsoap.org/soap/encoding/', location='http://schemas.xmlsoap.org/soap/encoding/')
	#imp.filter.add('http://ws.client.com/Members.asmx')
	#url = "http://www.brenda-enzymes.org/soap/brenda.wsdl"
	#imp = Import('http://www.w3.org/2001/XMLSchema')    # the schema to import.
	#imp.filter.add('http://microsoft.com/wsdl/types/')  # the schema to import into.
	#d = ImportDoctor(imp)

	#client = Client(url, doctor=d, cache=None)

	url = 'http://ws.tramtracker.com.au/pidsservice/pids'
	imp = Import('http://www.w3.org/2001/XMLSchema')    # the schema to import.
	imp.filter.add('http://microsoft.com/wsdl/types/')  # the schema to import into.
	d = ImportDoctor(imp)
	client = Client(url, doctor=d)
	
	password = hashlib.sha256(str("igembarcelona2016").encode('utf-8')).hexdigest()

	parameters = "joan.rue01@estudiant.upf.edu,"+password+",ecNumber*"+ecnumber+"#organism*"+organism+"#"

	if Km_or_Ki == "Km":
		resultString = client.service.getKmValue(parameters)
	elif Km_or_Ki == "Ki":
		resultString = client.service.getKiValue(parameters)
	else:
		raise ValueError('%s not found, try "Ki" or "Km"' % (Km_or_Ki))
	#print resultString

	all_instances = resultString.split('!')
	struct_instances = []
	#print "all_instances[0]: ", all_instances[0]

	for i,instance in enumerate(all_instances):
		
		properties = instance.split('#')

	#print properties[0]
		aux = dict()
		for element in properties:
			tmp = element.split('*')
			if len(tmp)==2:
				#print tmp[0]
				#c.update({tmp[0], tmp[1]})
				aux[tmp[0]] = tmp[1]

		struct_instances.append(aux)

	return struct_instances

print(search('Escherichia Coli','1.1.1.1','Ki'))

#print(hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest())