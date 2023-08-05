"""
Module practise
"""


def print_lol(some_list, level = 0):
    #Output all elements in a list-takes care of list of list too
    #recursive function
    for first_level in some_list:
        if isinstance(first_level, list):
            print_lol(first_level, level + 1)
        else:
            for tab_stop in range(level):
                print("\t", end="")
            print(first_level)
