#!/usr/bin/env python
# coding=utf-8
movies = ["The Holy Grail", 1975, "Terry Jone & Terry Gilliam", 91, 
                     ["Graham Chapman", ["michael Palin", "John Cleese", "Terry Gillliam"]]]
def print_lol(the_list, indent, level = 0):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end='')
                print(each_item)

print_lol(movies, True, 1)
