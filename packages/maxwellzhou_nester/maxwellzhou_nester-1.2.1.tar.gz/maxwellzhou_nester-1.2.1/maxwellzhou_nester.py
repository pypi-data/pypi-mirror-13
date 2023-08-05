def print_lol(the_list, level):
	for each_itme in the_list:
		if isinstance(each_itme, list):
			print_lol(each_itme, level + 1)
		else:
                        for tap_stop in range(level):
                                print("\t", end= ' ')
	                print(each_itme)
