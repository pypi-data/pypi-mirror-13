"""
list.py provides basic functionality of looping over the list
and check weather List contains another List and display them
"""
def print_lol(the_list):
            for each_item in the_list:
                        if isinstance(each_item, list):
                                    print_lol(each_item)
                        else:
                                    print(each_item)
                        
