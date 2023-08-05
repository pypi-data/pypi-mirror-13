"""
This is my module for practicing Python
"""

import sys

def print_lol(the_list, indent=False, level=0, write_dest=sys.stdout):
	"""
	This function takes a list, and prints it out. 
	If there is a nested list, it is printed out indented.
	"""
	for each_item in the_list: #first loop
		if isinstance(each_item, list):
			print_lol(each_item, indent, level+1, write_dest)
		else:
			if indent:	
				for ind in range(level):
					print('\t', end='', file=write_dest)
			print(each_item, file=write_dest)