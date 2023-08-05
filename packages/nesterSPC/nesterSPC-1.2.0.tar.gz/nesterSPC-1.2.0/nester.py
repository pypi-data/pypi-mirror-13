"""This module can be used to print inner lists in a list"""
def print_lol(the_list, level=0):
    """Iterate through each item in the list
       if the item is a list print the contents
       of that list. Else just print the non-listed
       items. A value can be assigned to indent
       each inner list."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end="")
            print(each_item)