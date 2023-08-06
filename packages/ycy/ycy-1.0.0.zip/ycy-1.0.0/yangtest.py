"""这是nester.py模块，提供了。。。嵌套列表"""
def print_lol(the_list):
    """这个函数取.....各占一行"""
    for each_one in the_list:
        if isinstance(each_one,list):
            print_lol(each_one)
        else:
            print(each_one)
