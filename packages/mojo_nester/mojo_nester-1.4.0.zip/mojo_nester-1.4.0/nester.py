import sys
def print_lol(the_list,indent=False,level=0,op=sys.stdout):
    """For iterative display list list"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1,op)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end=' ',file=op)
            print(each_item,file=op)
