"""
list.py provides basic functionality of looping over the list
and check weather List contains another List and display them
"""
movie = ["Don","Don2","Apathamitra","Upp2",["Actors",["Amithbh","Sharuk Khan","vishu","Upendra"]]]
def print_lol(the_list,myrange=0):
            for each_item in the_list:
                        if isinstance(each_item, list):
                                    print_lol(each_item,myrange+1)
                        else:
                                    for num in range(4):
                                                print("\t ",end =' ')
                                    print(each_item)
                        
