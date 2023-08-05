'''
这是模块注释
'''
'''
这是函数注释
'''
def print_lol(the_list):
	for item in the_list:
		if isinstance(item, list):
			print_lol(item)
		else:
			print(item)

