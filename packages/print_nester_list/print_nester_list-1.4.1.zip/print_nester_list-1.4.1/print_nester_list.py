"""这是nester.py模块，提供了一个名为print_lol（）的函数，
    这个函数的作用是打印列表，
    其中有可能包含（也可能不包含）嵌套列表"""

"""函数取一个位置参数，名为'the_list',
    可以是任何Pyhton列表（也可以是包含嵌套列表的列表）。
    所指定的列表中的每个数据项会（递归地）输出到屏幕上，各数据项占一行.
    第二个参数（名为level,缺省值为0）用来在遇到嵌套列表时插入制表符，
    第三个参数indent，用来指示是否打开缩进，True时缩进，False不缩进，默认为False,
    第四个参数fh，用来指示数据写入的位置，默认为标准输出"""
import sys

def print_lol(the_list,indent=False,level=0,fh=sys.stdout):           #level=0表示为level设置一个缺省值为0，用户可以不必传入该参数
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1,fh)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='',file=fh)
            print(each_item,file=fh)
