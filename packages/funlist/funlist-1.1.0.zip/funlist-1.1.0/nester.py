'''print_lol()函数，可以打印列表，其中有可能包含内嵌列表'''
'''the_list为参数，可以是任何Python列表。所指定的列表中每项会（递归地）输出到屏幕上，各数据项各占一行；
   第二个参数level用来遇到嵌套时插入制表符，添加一个缺省值，变成一个可选参数'''
def print_lol(the_list,level=0):
	for each_item in the_list:
		'''isinstance()用于检查某字符是否包含某特定类型的数据，返回True/False'''
		if isinstance(each_item,list):
			print_lol(each_item,level+1)
		else:
			for tab_stop in range(level):	#使用leve来控制使用多少个制表符
				print('\t',end='')	#每一层缩进都显示一个TAB制表符
			print(each_item)