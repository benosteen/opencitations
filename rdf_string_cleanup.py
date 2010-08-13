"""
rdf_string_cleanup.py 
"""

import re
import sys

# Cleanup a predicate
def predicate_cleanup (predicate, authorities):
	# Some syntax cleanup
	if re.search('^<.+>$', predicate):
		predicate = re.sub('^<(.+)>$', r'\1', predicate)
		
	# The PLoS triples often include the namespace authority in the predicate.
	# The namespace authority should be recorded with a prefix equivalent (see "authorities" list above);
	# then the predicate can be restated using the prefix
	if re.search('(http:.+[\/#])(.+?)$', predicate):
		m = re.search('(http:.+[\/#])(.+?)$', predicate)
		authority = m.group(1)
		predicateName = m.group(2)
		
		prefix = 0
		if authority in authorities.options('PLoS_authorities'):
			prefix = authorities.get('PLoS_authorities', authority)
		else:
			print "Don't recognise the authority " + authority + "\n"
		
		predicate = str(prefix) + ":" + str(predicateName)
		
	elif re.search('^http:', predicate):
		print "Can't break down the authority:predicate " + predicate + "\n"
	
	elif re.search(':', predicate):
		m = re.search('^(.+?):', predicate)
		prefix = m.group(1)
		
		if not prefix in list(y for x, y in authorities.items('PLoS_authorities') + authorities.items('PLoS_unauthorised')): # i.e. check whether the prefix can be found as a value anywhere in the authorities config
			print "Haven't defined the prefix " + prefix
	
	return predicate

# Cleanup a value; should work for both a string or a list
def value_cleanup (values, authorities=None):
	family_values = []
	
	#values could be either a list or a string. for ease of processing, if is a string we will treat it as a one-member list
	if isinstance(values, basestring):
		values = [values]
	
	for value in values:
		#Is is it a controlled vocabulary term?
		controlledVocab = 0
		if re.search('^<?([^:]+):[^:]+>?$', value):
			m = re.search('^<?([^:]+):[^:]+>?$', value)
			match = m.group(1)
			if authorities and ( match in list(y for x, y in authorities.items('PLoS_authorities') + authorities.items('PLoS_unauthorised') + authorities.items('Extras')) ): # i.e. is it a value anywhere in the authorities config
				value = re.sub("^<(.+)>$", r"\1", value)
				controlledVocab = 1
			elif not re.search("^['\"<].+['\">]$", value): #This is not controlled vocab, should be treated as a literal
				value = re.sub("^(.+)$", r'"\1"', value)
		# Some syntax cleanup
		elif re.search("^'.+'$", value):
			value = re.sub("^'(.+)'$", r'"\1"', value) #Change single quotes to doubles
		elif not re.search("^['\"<].+['\">]$", value): #Add quotes where they are needed
			value = re.sub("^(.+)$", r'"\1"', value)
			
		if re.search('(\n|\t|  )', value): #Normalise whitespace
			value = re.sub("(\n|\t|  )", " ", value)
			
		
		family_values.append(value)
	
	#Transform one-member list into a string
	if len(family_values)==1:
		family_values = family_values[0]
	
	return family_values