""" This is the "nester.py" module, and it provides one function called
print_lol(), which prints lists that way or may not include nested lists. """

# movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
# 	  ["Graham Chapman", ["Michael Palin", "John Cleese",
# 			      "Terry Gilliam", "Eric Idle", "Terry Jones"]]]

def print_lol(the_list, num_tabs):
    """ This function takes a positional argument called "the_list", which
    is any Python list (of possibly, nested lists). Each data item in the
    provided list is (recursively) printed to the screen on its own line """
    for each_item in the_list :
        if isinstance(each_item,list):
            print_lol(each_item, num_tabs+1)
        else :
            for tab in range(num_tabs):
                print("\t", end='');
            print(each_item)
