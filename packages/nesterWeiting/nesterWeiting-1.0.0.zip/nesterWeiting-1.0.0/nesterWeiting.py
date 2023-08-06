"""This is the "nesterWeiting.py" modual.by WeiTing"""
def print_lol(the_list):
    """This print_lol()function is written by WeiTIng"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
            
