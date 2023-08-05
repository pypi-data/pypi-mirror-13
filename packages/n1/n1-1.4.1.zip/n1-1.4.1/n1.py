"""This is the "n1.py" module and it provides on function called print_lol()
    which prints lists that may or may not include nested lists."""
import sys
def print_lol(the_list,indent=False,level=0,fh=sys.stdout):
    """If eg. print_lol(movie,True),this funcion takes one positional argument called "each_item" and one int 
        argument(choosible) called "level", where "the_list" is any Python list 
        (of - possibly - nested lists), "level" is the level of the n1.
        Each data item in theprovided list is (recursively) printed to the screen
        on it's own line, and the items in the i-th level will be printed after i 
        tabs"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1,fh)
        else:
                if indent:
                    for tab_stop in range(level):
                        print('\t',end='',file=fh)
                print(each_item,file=fh)
