"""this is,,"""
def print_lol(the_list,level=0):
    """jieshi"""
    for each_one in the_list:
        if isinstance(each_one,list):
            print_lol(each_one,level+1)
        else:
            for tab_stop in range(level):
                print ("\t",end='')
            print(each_one)
