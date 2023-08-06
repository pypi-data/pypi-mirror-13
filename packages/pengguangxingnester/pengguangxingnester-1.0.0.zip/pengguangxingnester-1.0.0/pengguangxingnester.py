#L=[1,2,['a','b','c',['A','B','C'],'d','e'],4,5]

def print_list(L):
	for i in L:
		if isinstance(i,list):
			print_list(i)
		else:
			print(i)
