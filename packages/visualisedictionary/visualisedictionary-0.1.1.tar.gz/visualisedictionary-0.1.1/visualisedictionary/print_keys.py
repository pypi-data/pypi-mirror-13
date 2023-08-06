#!/usr/bin/env python
'''
    Pretty printing for nested dictionaries
    :author: Alex Warwick Vesztrocy
'''


def pprint(d, _layer=''):
    '''
        This function pretty prints a nested python dictionary
    '''
    if isinstance(d, dict):
        # For each key in the current dictionary (layer)
        for k in d:
            # Print current key
            print(_layer + '- ' + k)

            # Recurse on this key's dictionary
            pprint(d[k], (_layer + '\t'))
