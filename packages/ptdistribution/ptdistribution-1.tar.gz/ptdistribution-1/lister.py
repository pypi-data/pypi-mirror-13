'''lister.py module'''
def print_lol(the_list):    
    for ti in the_list:
        if isinstance(ti,list):
            print_lol(ti)
        else:
            print(ti)
