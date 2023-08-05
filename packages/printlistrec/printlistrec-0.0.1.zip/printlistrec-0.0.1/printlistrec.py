
"""Function to recursively print list objects"""
def print_list(the_list):
    """Loop all items in the list"""
    for each_item in the_list:
        """If current item is a list itself call same function again"""
        if isinstance(each_item, list) :
            print_list(each_item)
        else:
            """else print the item"""
            print(each_item)
