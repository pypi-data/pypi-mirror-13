"""def"""
def printlist(listname):
	"""print"""
	for list1 in listname:
		if isinstance(list1,list):
			printlist(list1)
		else:
			print(list1)
