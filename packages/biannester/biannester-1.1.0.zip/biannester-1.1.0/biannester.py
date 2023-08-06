"""This is the"biannester.py" module and it provides one function called print_lol()
   which prints lists that may or may not include nested lists."""
def print_lol(the_list):
    """This function"""
    for each_item in the_list:
        if isinstance (each_item,list):
			print_lol(each_item,level+1)
	else:
                        for tab_stop in range(level):
				print("\t",end='')
			print(each_item)
   
