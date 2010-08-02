# http://code.activestate.com/recipes/52664/
# Created by Robin Parmar on Tue, 10 Apr 2001 (PSF)
# Modified by John Mansfield, IBRG, Oxford University
def Walk( root, recurse=0, pattern='*' ):
	import re, os
	
	# initialize
	result = []

	# must have at least root folder
	try:
		names = os.listdir(root)
	except os.error:
		return result

	# expand pattern
	pattern = pattern or '*'
	pat_list = pattern.split(';')
	
	# check each file
	for name in names:
		fullname = os.path.normpath(os.path.join(root, name))
		#print "NAME: " + name
		#print "PATH: " + fullname
		# grab if it matches our pattern and entry type
		for pat in pat_list:
			if re.search(pat, name):
				if os.path.isfile(fullname):
					result.append(fullname)
					#print "ADDING: " + fullname
				continue
				
		# recursively scan other folders, appending results
		if recurse:
			if os.path.isdir(fullname) and not os.path.islink(fullname):
				result = result + Walk( fullname, recurse, pattern )
			
	return result

