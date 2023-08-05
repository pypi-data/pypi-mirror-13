"""
	Module salad consists of one function print_lol()
"""


def print_lol(the_list):
	"""Function receives list as an argument and 
		prints it to standard output"""
	for el in the_list:
		if isinstance(el, list):
			print_lol(el)
		else:
			print(el)			