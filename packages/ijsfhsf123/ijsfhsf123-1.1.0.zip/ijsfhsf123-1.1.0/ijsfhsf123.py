def print_lol(the_list,level):
    for x in the_list:
        if isinstance(x,list):
            print_lol(x,level+1)
        else:
            for each_x in range(level):
                print("\t",end='')
            print(x)
