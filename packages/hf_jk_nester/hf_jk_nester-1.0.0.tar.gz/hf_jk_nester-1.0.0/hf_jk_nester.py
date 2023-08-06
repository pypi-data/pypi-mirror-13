"""

This is the "hf_jk_nester" module, it provides a function
called print_lol() which prints lists that may or may not
include nested lists.

Date: 19.02.2016
Author: Jaap Kroesschell

"""


def print_lol(ownList):
    """ This function takes a positional argument called "ownList",
    which is any Python list (of, possibly, nested lists).
     Each data item in the provided list is (recursively)
     printed to the screen on its own line. """

    for eachItem in ownList:
        if isinstance(eachItem, list):
            for eachNestedItem in ownList:
                if isinstance(eachNestedItem, list):
                    print_lol(eachNestedItem)
        else:
            print(eachItem)