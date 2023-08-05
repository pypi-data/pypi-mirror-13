# -*- coding: utf-8 -*-
"""模块的注释"""


def print_lol(the_list, indent = False, level = 0):
    """函数的注释"""
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, indent, level + 1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end='')
            print(item)

movies = [[1,2,['a', 'b', 'c']], "The Holy Grail", 1975, "The Life of Brian", 1979, "The Meaning of Life", 1983]
print_lol(movies)

