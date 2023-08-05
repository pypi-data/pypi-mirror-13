"""This is the "n1.py" module and it provides on function called f1()
    which prints lists that may or may not include nested lists."""
def f1(movie,indent=False,level=0):
    """If f1(movie,True),this funcion takes one positional argument called "a" and one int 
        argument(choosible) called "level", where "the_list" is any Python list 
        (of - possibly - nested lists), "level" is the level of the nester.
        Each data item in theprovided list is (recursively) printed to the screen
        on it's own line, and the items in the i-th level will be printed after i 
        tabs"""
    for a in movie:
        if isinstance(a,list):
            f1(a,indent,level+1)
        else:
                if indent:
                    for tab_stop in range(level):
                        print('\t',end='')
                print(a)
