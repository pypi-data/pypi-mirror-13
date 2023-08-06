# -*- coding: utf-8 -*-
"""This is the "nester.py" module and it provides one function called print_lol()"""

def print_lol(the_list, level=0):
    """This function takes one positional argument called "the_list"."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t"),
            print(each_item)

