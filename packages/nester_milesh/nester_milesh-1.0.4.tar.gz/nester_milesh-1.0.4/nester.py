import sys
"""Prints out Nested Lists"""

def print_lol(the_list, indent=True, level=0, target=sys.stdout):
        for an_entry in the_list:
                if isinstance(an_entry, list):
                        print_lol(an_entry, indent, level+1, target)
                else:
                        if (indent):
                                
                                for numTabs in range(level):
                                        print("\t", end='', file=target)
                        print(an_entry, file=target)


                        
