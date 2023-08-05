"""The module is for print
    the item in a nested list"""
#really
def print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item,list):
            """The item is a list"""
            print_lol(each_item)
        else:
            """The item is not a list"""
            print(each_item)
