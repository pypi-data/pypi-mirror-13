"""这是nester模块，这个模块的功能是打印出一个列表里的所有内容（包括嵌套的内容）"""
def print_lol(the_list,indent=False,level=0):
    """函数需要一个列表参数，当列表有嵌套的时候，需要迭代的调用该函数
	level参数提供了列表内部结构的展示，缺省值是0
	indent参数默认值为False，是是否缩进的开关"""
     for each_item in the_list:
        if(isinstance(each_item,list)):
           print_lol(each_item,indent,level+1)
        else:
            if indent: 
                for number in range(level):
                        print("\t",end='')
            print(each_item)
           
           
