"""This is the "nester.py" module and it provides one function called print_lol()"""

def print_lol(the_list):
    """This function takes one positional argument called "the_list"."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)

