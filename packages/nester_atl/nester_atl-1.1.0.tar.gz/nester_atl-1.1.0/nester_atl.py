#! /usr/bin/env python3
# -*- coding: utf8 -*-

"""This is the module of "nester.py", it provides a function named print_lol(),the role of the function
is to print a list"""
level=0
def print_lol(the_list, level):
    """The function takes a location parameter named "the_list" that is any list of python
    (Can also be a list containing nested lists).Each data item in the list specified will Recursive output 
    to the screen, and each data item for each."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for tab in range(level):
                print("\t", end='')
            print(each_item)

#"""Recursive function test.There gives a test list named "temp_list".
#If you run this file directly as main,it will run the following code,
#and use the function print_lol to recursive print the test list "temp_list"."""
#if __name__ == "__main__":
#    temp_list = [1, 32, 43, [12, 23, [123, 4321]], [2, 3, 4],[3, 5, 6, [1234, 234, 54, [23, 42, 43, 12, [23, 23, 2, 1231]]]]]
#    print_lol(temp_list, level)
