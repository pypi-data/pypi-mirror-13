"""这是"nester.py"模块，提供了一个名为print_lol()函数
    用来打印列表，其中包含或不包含嵌套列表。"""
def print_lol(the_list, level=0):
    """这个函数有一个位置参数，名为"the_list",
         这可以是任何Python列表（包含或不包含嵌套列表），
           所提供列表中的各个数据项会（递归地）打印到屏幕上，而且各占一行。
           第二个参数（名为"level")用来在遇到嵌套列表时插入制表符。"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for tab_step in range(level):
                print("\t", end='')
            print(each_item)
