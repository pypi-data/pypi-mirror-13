'''This is the "nester.py" module and it provides one funciont.....'''

def print_lol(the_list, level=0):
    '''This is function takes one positional argument called "the list", which
     is any python list'''
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level + 1)
        else:
            for tab_stop in range(level):
                print('\t', end='')
            print(each_item)
