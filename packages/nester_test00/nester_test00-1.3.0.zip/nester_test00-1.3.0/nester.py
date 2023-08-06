"""这是"nester.py"模块，提供一个print_lol()的函数，用来打印列表"""
def print_lol(the_list,level):
	"""第一个参数为要打印的列表，第二个参数为遇到嵌套列表时插入制表符的个数"""
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,level+1)
		else:
			for tab_num in range(level):
				print("\t",end='')
			print(each_item)
