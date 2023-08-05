"""this is the "nester.py" module and it provides one function called
print_lol() whih prints list that may or may not include nested lists"""

def print_lol(the_list, level=0):
    """this function takes one positional argument called "the_list", which
    is any python list (of - possibly - nested lists). Each data item in the
    provided list is (recursively) printed to the screen on its own line.
    A second argument called "level" is used to insert tab-stops when a nested
    list is encountered."""

    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end='' )
            print(each_item)
            
