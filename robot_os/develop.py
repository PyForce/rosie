#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 11:21:05 2015

@author: Toni
"""
import sys
PY_VERSION = sys.version_info[0] + 0.1*sys.version_info[1]

#---- Verifing python version ----
if PY_VERSION < 2.7:
    print('WARNING: Requires Python 2.7 or higher')
    exit()
    
print('Importing module: ordex')
try:
    from modules import ordex
    print('ordex... Ok')
except:
    print('ordex... Fail')
	
print('Importing module: kernel')
try:
    from modules.kernel import kernel
    print('kernel... Ok')
except Exception as e:
    print(e)
    print('kernel... Fail')

#---- Compatibility with Python2 ----
import code
interactive = code.InteractiveConsole()

# Start Process
command = ordex.Command()

#---- draw syntactic trees during the NLP ----
command.draw_syntactic_trees(False)

#---- enable log (default NLP.log) ----
#print('log: %s' % command.log_enable())
#
#base.log(' ','APP')
#base.log('******** START APP ********','APP')
#base.log(' ','APP')

while True:
    #---- input text ----
    st = interactive.raw_input("\nTEXT: ")
    print('')
    #---- process text ----
    cmd = command.extraction(st)
    if isinstance(cmd, ordex.base.Common_Commands):
        kernel.execute(cmd.CMD)
    elif isinstance(cmd, ordex.base.Urgent_Commands):
        pass
    else:
        print('ERROR: in module ordex')
