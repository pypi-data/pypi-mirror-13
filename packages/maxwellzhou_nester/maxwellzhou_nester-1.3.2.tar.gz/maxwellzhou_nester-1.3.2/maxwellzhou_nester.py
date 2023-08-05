import sys
def print_lol(the_list, indent = False, level = 0, fl = sys.stdout):
        for each_itme in the_list:
                if isinstance(each_itme, list):
                        print_lol(each_itme, indent, level + 1, fl)
                else:
                        if indent:
                                for tap_stop in range(level):
                                        print("\t", end= ' ', file=fl)
                        print(each_itme, file=fl)                       
