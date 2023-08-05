def print_lol(the_list,leval):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,leval+1)
		else:
			for tab in range(leval):
				print("\t",end='')
			print(each_item)