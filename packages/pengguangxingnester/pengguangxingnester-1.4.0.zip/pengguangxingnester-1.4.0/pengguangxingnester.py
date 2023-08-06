import sys
def print_list(L,indent=False,level=0,fn=sys.stdout):
	for i in L:
		if isinstance(i,list):
			print_list(i,indent,level+1,fn)
		else:
			if indent:
				for tab_stop in range(level):
					print('\t',end='',file=fn)
			print(i,file=fn)

