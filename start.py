#! /usr/bin/env python

try:
    print('Loading modules...')
    try:
        print('Importing module: ordex...')
        from modules import ordex
        print('ordex... Ok')
    except Exception as e:
        print(e)
        print('ordex... Fail')

    try:
        print('Importing module: kernel...')
        from modules.kernel import kernel
        print('kernel... Ok')
    except Exception as e:
        print(e)
        print('kernel... Fail')

    command = ordex.Command()
    command.draw_syntactic_trees(False)

    print('modules... Ok')
except Exception as e:
    print(e)
    print('modules... Fail')


from modules.WebHUD.manage import *

if __name__ == '__main__':
    run_server()

