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
def value_cleanup (values, authorities=0):
	family_values = []
	if isinstance(values, list):
		for value in values:
			# Some syntax cleanup
			if re.search("^'.+'$", value):
				value = re.sub("^'(.+)'$", r'"\1"', value) #Change single quotes to doubles
			elif not re.search("^['\"<].+['\">]$", value): #Add quotes where they are needed
				value = re.sub("^(.+)$", r'"\1"', value)
				
			if re.search('(\n|\t|  )', value): #Normalise whitespace
				value = re.sub("(\n|\t|  )", " ", value)
				
			#Check if it is a controlled vocab term erroneously surrounded by carats
			if re.search('^<([^:]+):[^:]+>$', value):
				m = re.search('^<([^:]+):[^:]+>$', value)
				match = m.group(1)
				if match in list(y for x, y in authorities.items('PLoS_authorities') + authorities.items('PLoS_unauthorised')): # i.e. is it a value anywhere in the authorities config
					value = re.sub("^<(.+)>$", r"\1", value)
			
			family_values.append(value)
	elif isinstance(values, basestring):
		# Some syntax cleanup
		if re.search("^'.+'$", values):
			values = re.sub("^'(.+)'$", r'"\1"', values) #Change single quotes to doubles
		elif not re.search("^['\"<].+['\">]$", values): #Add quotes where they are needed
			values = re.sub("^(.+)$", r'"\1"', values)
		if re.search('(\n|\t|  )', values): #Normalise whitespace
				values = re.sub("(\n|\t|  )", " ", values)
		
		#Check if it is a controlled vocab term erroneously surrounded by carats
		if re.search('^<([^:]+):[^:]+>$', values):
			m = re.search('^<([^:]+):[^:]+>$', values)
			match = m.group(1)
			if match in list(y for x, y in authorities.items('PLoS_authorities') + authorities.items('PLoS_unauthorised')): # i.e. is it a value anywhere in the authorities config
				values = re.sub("^<(.+)>$", r"\1", values)
		
		family_values = values
	
	return family_values