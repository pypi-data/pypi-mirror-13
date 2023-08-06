'''新手的第一次尝试'''
def print_lol(the_list):
	'''head first python'''
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item)
		else:
			print(each_item)
