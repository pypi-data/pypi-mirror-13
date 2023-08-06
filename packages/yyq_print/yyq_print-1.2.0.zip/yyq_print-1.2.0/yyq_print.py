"""这是一个完备版的模块，用户可以按原先使用习惯适应，即不缩进打印列表数据项，也可以缩进打印"""
def print_lol(the_list,indent = False,level = 0):
        """参数列表的后两个参数都定一个缺省值，没指定参数时会以缺省值执行"""
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,indent,level + 1)
		else:
                        if indent:
                                for tab_step in range(level):
                                        print "\t",
                        print each_item
