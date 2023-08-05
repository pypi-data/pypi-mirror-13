""" This is "luke_nester.py" module, which composes of a function "print_lol". """


def print_lol(the_list):
    """ This is function takes one positional argument called "the_list", which
        is any Python list (of possibly nested lists). Each data item in the
        provided list is (recursively) printed to the screen on it's own line."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
