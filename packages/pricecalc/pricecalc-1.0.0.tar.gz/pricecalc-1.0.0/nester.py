""" names = ['name1', 'name2', ['name31', 'name32', ['name331', 'name332', 'name333'], 'name33'], 'name4']
will use when needed """
""" commenting out code. Can be referred later
for each_name in names:
    if isinstance(each_name, list):
       for item in each_name:
           if isinstance(item, list): print('inner list')
           else: print(item)
    else:
        print(each_name)

"""

def print_names(each_list):
    for each_item in each_list:
        if isinstance(each_item, list):
            print_names(each_item)
        else:
            print(each_item)

""" print_names(names) - will use when needed"""


def print_names_level(each_list, level=0,indent=True,indlv=0):
    if level >= 1:
        for each_item in each_list:
            if isinstance(each_item, list):
                print_names_level(each_item,level-1,indent,indlv+1)
            else:
                print (int(indent)*"\t"*indlv,each_item)
                

"""the parameter indlv allows indentation levels. It is for internal
consumption and the function can be called without it

indent is Boolean i.e. 0 if False and 1 if True So the indentation
happens only when multiplied by 1"""

