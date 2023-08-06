"""this is,,"""
def print_lol(the_list,indent=False,level=0):
    """jieshi"""
    for each_one in the_list:
        if isinstance(each_one,list):
            print_lol(each_one,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print ("\t",end='')
            print(each_one)
