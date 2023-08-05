"""This scode prints on the shell the items of the list,
if there is nested item"""

def print_lol(the_list, level=0):
    for each_item in the_list:
        if isinstance(each_item, list):
            if level == 0:
                print_lol(each_item, level)
            else:
                print_lol(each_item, level+1)
            print_lol(each_item, level+1)
        else:
            for tab in range(level):
                print("\t", end='')
            print(each_item)
            
print_lol(movie, 0)
