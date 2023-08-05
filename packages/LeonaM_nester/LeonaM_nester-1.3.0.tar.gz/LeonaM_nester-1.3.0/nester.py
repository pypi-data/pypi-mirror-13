"""This is the "nester.py" module and it provides on function called print_lol()
    which prints lists that may or may not include nested lists."""
def print_lol(the_list, indent=False, level=0):
    """This funcion takes one positional argument called "the_list" and one int 
        argument(choosible) called "level", where "the_list" is any Python list 
        (of - possibly - nested lists), "level" is the level of the nester.
        Each data item in theprovided list is (recursively) printed to the screen
        on it's own line, and the items in the i-th level will be printed after i 
        tabs"""
        
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level + 1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end = '')
            print(each_item)
