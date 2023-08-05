import sys
"""
list.py provides basic functionality of looping over the list
and check weather List contains another List and display them
"""
movie = ["Don","Don2","Apathamitra","Upp2",["Actors",["Amithbh","Sharuk Khan","vishu","Upendra"]]]
def print_lol(the_list,indent =False ,level=0, fl=sys.stdout):
            for each_item in the_list:
                        if isinstance(each_item, list):
                                    print_lol(each_item,indent ,level+1,fl)
                        else:
                                    if indent:
                                                for num in range(level):
                                                            print("\t ",end =' ', file=fl)
                                    print(each_item, file=fl)
                        
