""" This is the "nester.py" module, and it provides one function called
print_lol(), which prints lists that way or may not include nested lists. """

# movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
# 	  ["Graham Chapman", ["Michael Palin", "John Cleese",
# 			      "Terry Gilliam", "Eric Idle", "Terry Jones"]]]

import sys

def print_lol(the_list, indent=False, level=0, fh=sys.stdout):
    """ This function takes a positional argument called "the_list", which
    is any Python list (of possibly, nested lists). Each data item in the
    provided list is (recursively) printed to the screen on its own line """
    for each_item in the_list :
        if isinstance(each_item,list):
            print_lol(each_item, indent, level+1, fh)
        else :
            if indent:
                for tab in range(level):
                    print("\t", end='', file=fh);
            print(each_item, file=fh)
