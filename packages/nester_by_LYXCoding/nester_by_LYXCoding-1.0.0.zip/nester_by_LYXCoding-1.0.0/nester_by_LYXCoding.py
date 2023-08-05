""" 定义一个函数，用来打印多层嵌套的列表"""

def print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
    
