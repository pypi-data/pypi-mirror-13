# -*- coding: utf-8 -*-
"""模块的注释"""

movies = [[1,2,['a', 'b', 'c']], "The Holy Grail", 1975, "The Life of Brian", 1979, "The Meaning of Life", 1983]


"""函数的注释"""
def print_lol(the_list):
    for item in the_list:
        if isinstance(item, list):
            print_lol(item)
        else:
            print(item)

print_lol(movies)
        


