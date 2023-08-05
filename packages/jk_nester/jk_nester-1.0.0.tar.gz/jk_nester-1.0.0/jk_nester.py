"""
Module practise
"""


def print_lol(some_list):
    #Output all elements in a list-takes care of list of list too
    #recursive function
    for first_level in some_list:
        if isinstance(first_level, list):
            print_lol(first_level)
        else:
            print(first_level)
