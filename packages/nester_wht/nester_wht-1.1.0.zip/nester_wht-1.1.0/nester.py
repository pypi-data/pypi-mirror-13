def print_lol(the_list, level):
    '''
	打印列表
	并且在嵌套列表时加入制表符
	'''
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each_item)
            
