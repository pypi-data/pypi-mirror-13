"""

This is the "hf_jk_nester" module, it provides a function
called print_lol() which prints lists that may or may not
include nested lists.

Date: 19.02.2016
Author: Jaap Kroesschell

"""


def print_lol(ownlist, indent=False, level=0):
    """ This function takes a positional argument called "ownList",
    which is any Python list (of possibly, nested lists).
     Each data item in the provided list is (recursively)
     printed to the screen on its own line.
     A second argument enables tabbed printing in case of nested lists.
     A third argument called "level" is used to insert tab-stops
     when a nested list is encountered. """

    for eachItem in ownlist:
        if isinstance(eachItem, list):
            print_lol(eachItem, indent, level+1)
        else:
            if indent == True:
                for tab_stop in range(level):
                    print('\t', end='')
            print(eachItem)