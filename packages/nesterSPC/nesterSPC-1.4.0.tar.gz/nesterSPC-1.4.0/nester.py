"""
Description:
    This module can be used to print inner lists in a list.
    
    --Updates--
    2016-01-02: Added a new option argument that allows a
                specified output file.  By default it will
                print to screen.
    2016-01-02: Added a new optional argument that allows 
                the user to enable the indenting function.
                It is turned off by defualt.
    2016-01-02: Added an optional level argument which is
                defaulted to 0. This indents each list by
                the value specified.
    2016-01-01: Initial write             
"""
def print_lol(the_list, indent=False, level=0, output=sys.stdout):
    """Iterate through each item in the list
       if the item is a list print the contents
       of that list. Else just print the non-listed
       items. A value can be assigned to indent
       each inner list. By default the indentation
       is turned off."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1, output)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t" * level, end="", file=output)
            print(each_item, file=output)