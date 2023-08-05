def print_lol(this_list, level):
        for list_item in this_list:
                if isinstance(list_item, list):
                        print_lol(list_item, level+1)
                else:
                        for tab_stop in range(level):
                                print('\t',end='')
                        print(list_item)
