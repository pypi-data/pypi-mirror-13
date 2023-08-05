def print_lol(the_list, indent = False, num = 0, output = sys.stdout):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item, indent, num+1, output)
		else:
                    if indent:
                        for number in range(num) :
                                print("\t",end='', file = output)
                    print(each_item, file = output)
