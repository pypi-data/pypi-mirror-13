def print_lol(the_list, num = 0):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item, num+1)
		else:
                        for indent in range(num):
                                print("\t",end='')
                        print(each_item)
