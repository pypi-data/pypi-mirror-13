#aaaaaa
"""aaa"""

def print_lol(the_list):
    for x in the_list:
        if isinstance(x,list):
            print_lol(x)
        else:
            print(x)
