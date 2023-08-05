def print_lol(this_list, indent='false', level=0):
        for list_item in this_list:
                if isinstance(list_item, list):
                        print_lol(list_item, indent, level+1)
                else:
                        if indent:
                                for tab_stop in range(level):
                                        print("\t",end='')
                        print(list_item)
