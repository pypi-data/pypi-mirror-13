"""
Given a list, this recorsive function prints out on the shell
the items of the list.
If there are nested lists, then this function will recurse and
iterate through the items of the list, so that all the elements
will be printed out.
"""

def print_lol(the_list):
    for item in the_list:
        if isinstance(item, list):
            print_lol(item)
        else:
            print(item)
