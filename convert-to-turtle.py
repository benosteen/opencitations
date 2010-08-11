"""
convert-to-turtle.py 

Read RDF data in XML or any triples format, does some cleanup, and outputs as Turtle RDF
"""

import sys, re, os
from read_triples import read_triples
from dir_navigator import Walk
from check_fulltext import check_fulltext
from restructure_data import restructure_data

# Creates custom sort-keys, so that graphs can be output in an order more readable for humans
def sort_graphs(subject):
	graphType = 0
	
	if triples[subject].has_key('rdf:type'):
		if triples[subject].has_key('cito:cites'):  #It's the citing article graph
			graphType = '00-'
		elif triples[subject]['rdf:type']=='fabio:Document': #It's an article - either a cited article, or an article that abstract that simply has no citations
			graphType = '01-'
		elif '<http://purl.org/net/nknouf/ns/bibtex#Article>' in triples[subject]['rdf:type']: # Also an article
			graphType = '01-'
		elif triples[subject]['rdf:type']=='foaf:Person': #It's an author graph
			graphType = '02-'
		else:
			print "Graph type unknown"
			graphType = '99-'
		
	sortKey = str(graphType) + str(subject)
	return sortKey

# As above, but sort rules for predicates
def sort_predicates(predicate):
	sortKey = 0
	
	if predicate=='rdf:type':  # rdf:type first
		sortKey = '00'
	elif predicate=='dc:creator':  # then author(s)
		sortKey = '01'
	elif predicate=='frbr:partOf':  # put partOf relation to the end, because it nests into a subgraph
		sortKey = 'zz'
	else:
		sortKey = predicate # All other predicates just get sorted according to their actual name
	
	return sortKey

def print_indent (depth):
	indent = 0
	while indent < depth:
		outputFile.write('\t')
		indent += 1

# A recursive function, that prints out dictionary contents, and recurses through sub-dictionaries
def print_dictionary (dict, depth):
	for key in sorted(dict.keys(), key=sort_predicates):
		print_indent(depth)
		outputFile.write(key + '\t')
		if type(dict[key]).__name__=='str':
			toprint = dict[key]
			outputFile.write(toprint + ';\n')
		elif type(dict[key]).__name__=='list':
			toprint = ", ".join(dict[key])
			outputFile.write(toprint + ';\n')
		elif type(dict[key]).__name__=='dict':
			depth += 1
			outputFile.write('[\n')
			print_dictionary(dict[key], depth)
			print_indent(depth-1)
			outputFile.write(']\n')
			depth -= 1
		else:
			"Unexpected data type for output value: " + str(type(dict[key]).__name__)
			
def output_turtle (triples):
	hasMetadata = hasRefs = 0
	for subject in sorted(triples.keys(), key=sort_graphs): #Uses our custom sort function
		outputFile.write(subject + "\n")
		
		if triples[subject].has_key('dc:creator'):
			hasMetadata = 1  # At least some article metadata has been recorded
			
		if triples[subject].has_key('cito:cites'):
			hasRefs = 1  # At least some references have been recorded
		
		pos = 0 #position as we cycle through the list of keys
		for predicate in sorted(triples[subject].keys(), key=sort_predicates): # Another custom sort
			values = triples[subject][predicate]
			
			outputFile.write("\t" + predicate + "\t") 
			# # # Here we are going to make sure the output value is a string
			if type(values).__name__=='dict':
				outputFile.write('[\n')
				print_dictionary(values, depth=2) #Send it to a recursive dictionary printer (can go as deep as required)
				print_indent(depth=1)
				outputFile.write(']')
			elif type(values).__name__=='str':
				outputFile.write(values)
			elif type(values).__name__=='list':
				outputFile.write(", ".join(values))
			else:
				print "Unexpected data type for output value: " + str(type(values).__name__)
			
			
			#Last one should be followed by full stop
			if pos + 1 == len(triples[subject].keys()):
				outputFile.write(".\n\n")
			
			#All others use a semi-colon
			else:
				outputFile.write(";\n")
			
			pos += 1
	
	return(hasMetadata, hasRefs)


# # # # # # # # #
# MAIN PROCESS! # 
# # # # # # # # #

#Provide command-line arguments: input-file, input-format
if not len(sys.argv)==3:
	sys.exit("Program requires two command-line arguments: 1) top-level directory for source data; 2) source file format\n")

sourceDir = sys.argv[1]
inputFormat = sys.argv[2]

print "Source directory: " + str(sourceDir) + "..."
print "Input format: " + str(inputFormat) + "..."
if not re.search('(xml|triple)', inputFormat, re.IGNORECASE):
	sys.exit("Input format can't be identified\n")

# Go through source directoy structure, making transformed version of every source file
sourceFiles = [] 
if re.search('xml', inputFormat, re.IGNORECASE):
	sourceFiles = Walk(sourceDir, 1, '^.+\.n?xml$')
elif re.search('triple', inputFormat, re.IGNORECASE):
	sourceFiles = Walk(sourceDir, 1, "^.+.txt$")
	
outputDir = re.sub('/$', '', sourceDir)
outputDir = outputDir + '_Turtle-RDF/'
if not os.path.isdir(outputDir):
	os.makedirs(outputDir) #NB this function makes all intermediate dirs as required

articlesReport = open(outputDir + 'articles_report.txt', 'w')
#Print a header to the output file
articlesReport.write ("""######
	## Report on data processing by convert-to-turtle.py 
	## at the Open Citations Project, Image Bioinformatics Research Group,
	## University of Oxford. See http://ibrg.zoo.ox.ac.uk
	######

""")

for inputFileName in sorted(sourceFiles):
	print "Doing file: " + str(inputFileName) + "..."

	#Output filename is same as input, but with changed top-level directory, and changed file extension
	outputFileName = re.sub(sourceDir, outputDir, inputFileName)
	outputFileName = re.sub('\.(txt|xml|nxml)$', '', outputFileName)
	outputFileName = outputFileName + ".n3"
	
	outputPath = re.sub('/[^/]+$', '/', outputFileName)
	#print outputPath
	if not os.path.isdir(outputPath):
		os.makedirs(outputPath) #NB this function makes all intermediate dirs as required
	
	#Filehandles
	inputFile = open(inputFileName, 'r')
	outputFile = open(outputFileName, 'w')

	#Print a header to the output file
	outputFile.write ("""######
	## Turtle RDF data, generated using convert-to-turtle.py 
	## at the Open Citations Project, Image Bioinformatics Research Group,
	## University of Oxford. See http://ibrg.zoo.ox.ac.uk
	######

	""")
	outputFile.write ("## Source file: " + str(inputFileName) + "\n\n")
	
	from MyConfigParser import MyConfigParser  #Uses my own modified version of ConfigParser, to facilitate character escaping
	#Get namespace authorities from separate manifest
	authorities = MyConfigParser()
	authorities.read('namespace_authorities.cfg')

	#List all the authority prefixes at the top of the output file
	for section in authorities.sections():
		for auth in authorities.options(section):
			outputFile.write("@prefix\t" + authorities.get(section, auth) + ":\t<" + auth + ">.\n")

	outputFile.write("\n")

	#Read the inputFile in to a triples dictionary. In fact it will be a multidimensional dictionary, taking the form triples[subject][predicate]
	triples = read_triples(inputFile, inputFormat, authorities)
	
	#Restructure data graphs, one by one
	for graph in triples.keys():
		triples[graph] = restructure_data(triples[graph])

	#Check whether input article (if it is an xml document) contains fulltext
	inputFile = open(inputFileName, 'r')
	hasFulltext = 0
	if re.search('xml', inputFormat, re.IGNORECASE):
		hasFulltext = check_fulltext(inputFile)
	
	# Output the rdf triples data
	# (And record these flags as you do so)
	(hasMetadata, hasRefs) = output_turtle(triples)
		
	# Reporting
	inputFileName = re.sub('^[^/]+/', '', inputFileName)
	articlesReport.write(str(inputFileName) + "\t")
	if hasMetadata==1:
		articlesReport.write("got_metadata" + "\t")
	else:
		articlesReport.write("NO_metadata" + "\t")
		
	if hasFulltext==1:
		articlesReport.write("got_fulltext" + "\t")
	else:
		articlesReport.write("NO_fulltext" + "\t")
	
	if hasRefs==1:
		articlesReport.write("got_references" + "\n")
	else:
		articlesReport.write("NO_references" + "\n")

	inputFile.close()
	outputFile.close()

articlesReport.close()
