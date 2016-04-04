# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 11:02:54 2015

@author: Toni
"""

#### IMPORT ####
from ... import base
from . import preprocess, process

class English():
    """
    Order extraction of the English language.
    """
    
    def __init__(self):
        pass
    
    def extraction(self, text=''):
        """
        Order extraction.
        
        :param text: orders
        :type text: str
        :return: list of commands
        :type: list(list(dict))
        
        >>> English.extraction("stop in the hall")
        [[{'start': None, 'end': None}, {'pos': 'in', 'place': 'hall'}, {'action': 'stop'}]]
        """
        base.log(text,'NLP_EN')
        sentences=preprocess.preprocess(text)
        base.log(sentences,'NLP_EN') 
        process.COMMAND_CMD=[]
        process.process(sentences)
        if process.COMMAND_CMD:
            return process.COMMAND_CMD[:]
        return []