def print_data(the_list,level=0):
	for each_element in the_list:
		if isinstance(each_element,list):
			print_data(each_element,level+1)
		else:
			for tab in range(level):
				print("\t")
			print(each_element);