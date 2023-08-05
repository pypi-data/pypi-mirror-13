'''
该模块是《Head First Python》一书中对应的学习例子
'''
'''
该方法主要用于打印一个多级列表，把每级列表的元素一一打印出来。
额外功能：
1. 可以给元素的前面加上任意多个制表符；
2. 可以实现不同级别的元素显示为不同的缩进；
3. 可以指定输出的位置
'''
import sys

def print_lol(the_list, flag=False, tab_num=0, out=sys.stdout):
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, flag, tab_num+1, out)
        else:
            if flag:
                for i in range(tab_num):
                    print("\t", end="", file=out)
            print(item, file=out)
