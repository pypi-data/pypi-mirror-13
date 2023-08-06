"""This module prints each item within a list, taking care of also printing items within nested lists"""

def print_lol(the_list):

    
	for each_item in the_list:
		if isinstance(each_item, list): 
			print_lol(each_item)
		else: 
			print(each_item)
