from bioservices.kegg import KEGG
# More info at https://pythonhosted.org/bioservices/kegg_tutorial.html#kegg-tutorial


# We generate a KEGG object (no frekin idea what is it)
k = KEGG()

# We assign our desired organism (by their three letters code: ecoli = "eco", human = "hsa,...) to our KEGG obj
k.organis = "eco" #Yeah? Organis is correct?

# k.lookfor_pathway("B Cell") # Self explicative

k.pathwayIds # Shows all (all?) patwhays IDs of our organism

#a = k.get("path:eco04122") # Example of "getting" a pathway
#a = k.parse_kgml_pathway("eco04122") #Get the pathway and parse it


