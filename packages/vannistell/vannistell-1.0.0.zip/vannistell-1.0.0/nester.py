"""Module for the function that flattens nested lists"""
def print_lol(the_list):
        for each_item in the_list:
                """a function that flattens nested lists"""
                if isinstance(each_item, list):
                        print_lol(each_item)
                else:
                        print(each_item)
