import sys
def print_lol(the_list, indent=False, level=0, fh=sys.stdout):
                    for each in the_list:
                            if isinstance(each, list):
                                print_lol(each,indent,level+1, fh)
                            else:
                                if indent:
                                 for tab_stop in range(level):
                                    print("\t",end=' ', file=fh)
                                 print(each,file=fh)
                                    
                                    
                                    
