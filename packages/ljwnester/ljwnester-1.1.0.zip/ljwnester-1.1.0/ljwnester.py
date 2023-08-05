def print_list(listype,level):
        for each_item in listype:
                if isinstance(each_item,list):
                        print_list(each_item,level+1)
                else:
                        for tab_stop in range(level):
                                print("\t",end='')
                        print(each_item)
			
