__author__ = 'Meng'
"""
this is the first python code learned from Head First Python
using for printing full format of the movie comment by iterating way
"""


def print_lol(movies,indent=False,level=0):

    for each_item in movies:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each_item)