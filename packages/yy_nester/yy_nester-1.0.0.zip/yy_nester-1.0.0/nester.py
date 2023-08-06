#movies =["the holy grail","1975","thrry jones & terry","345",91,["graham chapman",["michael palin","jone cleese",]]]
"""这是个名为lianxi1.py的模块，提供一个名为print_lol()的函数。"""
def print_lol(the_list):
    for each_item in the_list:
        if isinstance (each_item,list):
            
                print_lol(each_item)
        else:
            print(each_item)
#print_lol(movies)
