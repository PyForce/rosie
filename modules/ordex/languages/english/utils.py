# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 14:01:40 2015

@author: Toni
"""

from . import dictionary

def keyword(word,parameter='action'):
    """
    Dictionary of keywords in the extraction of commands for the mobile robotics.
    
    :param text: tagged token sequence of words
    :type text: tuple(str, str)
    :return: keyword
    :type: str
    
    >>> keyword(('go','VB'))
    'move'
    """
    try:
        return dictionary._KEYWORDS[parameter][word[0].lower()]
    except: return None