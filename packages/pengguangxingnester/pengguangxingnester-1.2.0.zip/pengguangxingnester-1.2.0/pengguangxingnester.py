#L=[1,2,['a','b','c',['A','B','C'],'d','e'],4,5]

def print_list(L,level=0):
	for i in L:
		if isinstance(i,list):
			print_list(i,level+1)
		else:
			for tab_stop in range(level):
				print('\t',end='')
			print(i)
