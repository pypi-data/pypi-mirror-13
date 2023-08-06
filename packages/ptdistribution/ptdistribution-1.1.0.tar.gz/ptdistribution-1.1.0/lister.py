'''lister.py module'''
def print_lol(the_list,level):
    for ti in the_list:
        if isinstance(ti,list):
            level=level+1
            print_lol(ti,level)
        else:
            for tab in range(level):
             print("\t",end='')
            print(ti)
