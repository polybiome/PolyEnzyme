# SOME IMPORTS

import requests


# TO SEE ALL DOCS IN DATABASE
database_url = 'https://rawgit.com/polybiome/database/master/README.md'  #MILLOR NO UTILITZAR EL README
database = requests.get(database_url)
database = database.content
database = database.decode().split('> ')
database = database[1:]
prompt_text = "Enter the number for the desired file \n [0] > Go Back"
for i, file in enumerate(database):
    database[i] = file.replace(' ','')
    database[i] = file.replace('\n','')
    prompt_text = prompt_text + " \n [%d] > %s" %(i+1,file)

choice = int(input(str(prompt_text)))  # SI NO VOLS UN RAW INPUT ES POT FER AMB BOTONS

if choice:
    url = 'https://rawgit.com/polybiome/database/master/%s' % database[choice-1]
    r = requests.get(url)
    textfile = r.text  # temporary, try to decode json directly
    print(textfile)

else: 
    pass  #Go back to menu