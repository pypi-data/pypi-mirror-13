def print_list(the_list):
	for each_list in the_list:
		if isinstance(each_list,list):
			print_list(each_list)
		else:
			print(each_list)