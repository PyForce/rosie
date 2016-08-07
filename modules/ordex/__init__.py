# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 11:02:54 2015

@author: Toni
"""
from . import base
from .languages import english


__all__ = ['__author__', '__credits__', '__version__', 'Command']

###### INFORMATION ######
__author__ = 'Antonio Serrano Muñoz <asm.holguin@gmail.com, toni.sm@nauta.cu>'
__credits__ = ('Silvia María Rodríguez-Ojea Picos <ojeasm@gmail.com>')
__version__ = '1.12'

###### IMPORT ######

###### CLASS ######


class Command(object):

    def __init__(self):
        self.english = english.English()

    def draw_syntactic_trees(self, draw=True):
        """
        Draw the syntactic trees during the NLP

        :param draw: True/False
        :type draw: bool
        """
        base.DRAW = draw

    def extraction(self, text=''):
        """
        Order extraction.

        :param text: orders
        :type text: str
        :return: commands
        :type: list

        >>> Command.extraction("go to the door")
        [{'start': None, 'end': None, 'pos': 'to', 'place': 'door',
          'action'='stop'}]
        """
        base.log(' ', 'NLP')
        cmd = []
        if text:
            if base.LANGUAGE == 'EN':
                print(' Extracting order from: %s' % repr(text))
                cmd = self.english.extraction(text)
            if cmd:
                base.log(cmd, 'NLP')
                return base.Common_Commands(cmd)
        return []

    def log_config(self, name='NLP', path=''):
        """
        Setup log.

        :param name: name of the log file
        :type name: str
        :param path: path of the log file
        :type path: str
        :return: path of the log file
        :type: str
        """
        base.log_config(name, path)
        return base.LOG_PATH

    def log_enable(self, enable=True):
        """
        Enable the register in the log file.

        :param enable: True/False
        :type enable: bool
        """
        base.log_enable(enable)
        return base.LOG_PATH

    def user(self, user='User'):
        """
        User that set a order.

        :param user: username
        :type user: str
        """
        base.USER = user


def init():
    import sys
    from kernel import handler
    handler._ordex(sys.modules['ordex'])
