def print_list(the_list, level):
	for each_list in the_list:
		if isinstance(each_list,list):
			print_list(each_list,level+1)
		else:
			for each_level in range(level):
				print("\t",end='')
			print(each_list)