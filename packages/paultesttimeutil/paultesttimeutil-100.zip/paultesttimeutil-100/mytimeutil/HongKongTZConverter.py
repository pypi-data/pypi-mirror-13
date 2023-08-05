'''
Created on Dec 29, 2015

@author: 1435188
'''

import pytz

def from_native_to_hk(t):
    '''
    Assume t is UTC if its tzinfo is None
    '''
    if t.tzinfo is None:
        t = t.replace(tzinfo = pytz.UTC)
    t3 = t.astimezone(pytz.timezone('Hongkong'))
    return t3

