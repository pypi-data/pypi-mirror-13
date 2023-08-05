def print_lol(the_list, level):
	for each_itme in the_list:
		if isinstance(each_itme, list):
			print_lol(each_itme, level + 1)
		else:
			print(each_itme)
