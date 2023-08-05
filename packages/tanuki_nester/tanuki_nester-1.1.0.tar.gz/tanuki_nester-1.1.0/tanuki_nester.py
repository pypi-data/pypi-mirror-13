"""This module is made for printing multi_deep_list"""

def print_lol(the_list,level):
	for each_item in the_list:
		if isinstance(each_item) :
			print_lol(each_item,level+1)
		else:
			for tab_stop in range(level):
				print("\t", end='')
			print(each_item)
