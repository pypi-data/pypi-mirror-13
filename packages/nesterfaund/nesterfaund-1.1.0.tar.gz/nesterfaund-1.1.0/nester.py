"""
nester module, provide a function named print_lol()
"""
def print_lol(the_list, level):
    """
    print_lol(the_list, level), the_list can be any python list
    it also can be a nested list
    """

    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(each_item)
