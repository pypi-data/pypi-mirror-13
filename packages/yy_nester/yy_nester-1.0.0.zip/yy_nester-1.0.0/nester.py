#movies =["the holy grail","1975","thrry jones & terry","345",91,["graham chapman",["michael palin","jone cleese",]]]
"""���Ǹ���Ϊlianxi1.py��ģ�飬�ṩһ����Ϊprint_lol()�ĺ�����"""
def print_lol(the_list):
    for each_item in the_list:
        if isinstance (each_item,list):
            
                print_lol(each_item)
        else:
            print(each_item)
#print_lol(movies)
