"""
convert-to-turtle.py 

Read RDF data in XML or any triples format, does some cleanup, and outputs as Turtle RDF
"""

import sys, re, os
from read_triples import read_triples
from namespace_authorities import get_nsAuthorities
from output_vocabulary import get_vocabulary
from dir_navigator import Walk
from check_fulltext import check_fulltext

# Creates custom sort-keys, so that graphs can be output in an order more readable for humans
def sort_graphs(subject):
	graphType = 0
	
	if triples[subject]['entityType']=='fabio:Document' and triples[subject].has_key('references'):  #It's the citing article graph
		graphType = '00-'
	elif triples[subject]['entityType']=='fabio:Document': #It's an article - either a cited article, or an article that abstract that simply has no citations
		graphType = '01-'
	elif triples[subject]['entityType']=='foaf:Person': #It's an author graph
		graphType = '02-'
	else:
		print "Graph type unknown"
		graphType = '99-'
		
	sortKey = graphType + str(subject)
	return sortKey

# As above, but sort rules for predicates
def sort_predicates(predicate):
	sortKey = 0
	
	if predicate=='entityType':  # rdf:type first
		sortKey = '00'
	elif predicate=='artAuthor':  # then author(s)
		sortKey = '01'
	elif predicate=='refAuthor':  # author(s)
		sortKey = '02'
	else:
		sortKey = predicate # All other predicates just get sorted according to their actual name
	
	return sortKey

def output_turtle (triples):
	hasMetadata = hasRefs = 0
	for subject in sorted(triples.keys(), key=sort_graphs): #Uses our custom sort function
		outputFile.write(subject + "\n")
		
		if triples[subject].has_key('artAuthor'):
			hasMetadata = 1  # At least some article metadata has been recorded
			
		if triples[subject].has_key('refAuthor'):
			hasRefs = 1  # At least some references have been recorded
		
		pos = 0 #position as we cycle through the list of keys
		for predicate in sorted(triples[subject].keys(), key=sort_predicates): # Another custom sort
			values = triples[subject][predicate]
			# # # Here we are going to make sure the output value is a string
			if type(values).__name__=='dict':
				valueList = []
				for key in values.keys():
					value = 0
					if type(values[key]).__name__=='str':
						value = values[key]
					elif type(values[key]).__name__=='list':
						value = str(", ".join(values[key]))
					displayKey = str(get_vocabulary(key))
					valueList.append(displayKey + ' "' + value + '"')
				valueString = "[\n\t\t" + str(";\n\t\t".join(valueList)) + "\n\t]"
				values = valueString
			if type(values).__name__=='str':
				values = values #It's already a string
			elif type(values).__name__=='list':
				values = str(", ".join(values))
			else:
				print "Unexpected data type for output value: " + str(type(values).__name__)
			# # #
				
			displayPredicate = str(get_vocabulary(predicate))
			outputFile.write("\t" + displayPredicate + "\t" + values)
			
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

	#Get namespace authorities from separate manifest
	authorities = get_nsAuthorities()

	#List all the authority prefixes at the top of the output file
	for auth in sorted(authorities.keys()):
		outputFile.write("@prefix\t" + authorities[auth] + "\t<" + auth + ">.\n")

	outputFile.write("\n")


	#Read the inputFile in to a triples dictionary. In fact it will be a multidimensional dictionary, taking the form triples[subject][predicate]
	triples = read_triples(inputFile, inputFormat, authorities)

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
