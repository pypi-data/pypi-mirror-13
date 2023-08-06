"""This is multiline comment
nester.py module"""
def print_lol(the_list, level=0):
    """this function takes one positional
    argument and checks if it is a list-type and """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(each_item)
