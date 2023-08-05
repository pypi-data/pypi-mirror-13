__author__ = 'yg.jang'

"""
THis si the "nester.py" module and it provides one function called print_lol()
which prints lists that may or may not include nested lists.
"""


def print_lol(the_list, indent=False, level=0):
    """
     This function takes one positional argument calloed "the_list", which
    is any Python list (of - possibly - nested lists). Each date item in the
    provided list is (recursively) printed to the screeen on it's own line.
    - add indent printable function
    - add select indent or not indent using 'indent' Flag
    :param the_list:
    :param indent:
    :param level:
    :return:
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1)
        else:
            if indent:
                for tab in range(level):
                    print("\t", end='')
            print(each_item)
