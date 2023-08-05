# Print nested lists
"""
Hello guys, this module prints list and any of the nested list or lists
within lists
"""
# Sample List
"""
movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
["Graham Chapman",["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]
"""

def print_lol(the_list,level=0):
    """
     This function checks whether there is nested list associated
     with each item or nested list within a nested list using the
     phenomenon of recursion
    """

    for each_item in the_list:
        if isinstance(each_item,list):
         print_lol(each_item,level+1)
        else:
         for tab_space in range(level):
          print("\t",end='')
         print(each_item)
