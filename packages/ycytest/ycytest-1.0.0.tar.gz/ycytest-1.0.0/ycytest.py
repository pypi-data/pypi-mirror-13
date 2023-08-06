"""this is,,"""
def print_lol(the_list):
    """jieshi"""
    for each_one in the_list:
        if isinstance(each_one,list):
            print_lol(each_one)
        else:
            print(each_one)
