"""
nester module, provide a function named print_lol()
"""
def print_lol(the_list, indent=False, level=0):
    """
    print_lol(the_list, level), the_list can be any python list
    it also can be a nested list
    """

    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1)
        else:
            if indent:
                print("\t" * level, end='')
            print(each_item)
