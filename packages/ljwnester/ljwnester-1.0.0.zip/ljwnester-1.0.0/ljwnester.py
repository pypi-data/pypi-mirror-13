def print_list(listype):
	for each_item in listype:
		if isinstance(each_item,list):
			print_list(each_item)
		else:
			print(each_item)
