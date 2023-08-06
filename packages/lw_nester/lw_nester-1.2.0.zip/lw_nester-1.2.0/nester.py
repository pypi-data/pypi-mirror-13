'''This is the "nester.py" module and it provide a function called print_lol()
   which prints lists that may or may not include nested lists.'''
def print_lol(the_list，level=0):
    '''This funciton takes a positional argument called "the_list", which
       is any Python lists (of - possibly - nested lists). Each data item in
       the provided list is recursively printed to the screen on its own line.
       A second argument called "level" used to insert tab-stops when a nested
       list is encountered.'''
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, level+1)
        else:
            for tab_stop in range(level):
                print('\t', end='')
            print(item)


