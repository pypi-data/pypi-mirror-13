def print_lol(the_list,level):
	for a in the_list:
		if isinstance(a,list):
			print_lol(a,level+1)
		else:
			for b in range(level):
				print("\t",end='')
			print(a)
