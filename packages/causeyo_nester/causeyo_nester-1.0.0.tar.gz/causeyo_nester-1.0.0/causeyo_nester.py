"""This is multiline comment
nester.py module"""
def print_lol(the_list):
    """this function takes one positional
    argument and checks if it is a list-type"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
