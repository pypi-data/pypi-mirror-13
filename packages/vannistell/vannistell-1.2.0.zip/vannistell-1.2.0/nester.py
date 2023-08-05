def print_lol(the_list,indent):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent+1)	#Adds an additional tab space when a nested list is encountered
        else:
            for tabs in range(indent):
                print("\t",end='')
            print(each_item)

