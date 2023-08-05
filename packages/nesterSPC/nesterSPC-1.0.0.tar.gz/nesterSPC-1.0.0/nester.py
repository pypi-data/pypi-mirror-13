"""This module can be used to print inner lists in a list"""
def print_lol(the_list):
    """Iterate through each item in the list
       if the item is a list print the contents
       of that list. Else just print the non-listed
       items"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)