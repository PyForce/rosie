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

print('Starting rOSi...') #TODO: remove at least a `print`
print('Importing module: WebHUD')
from modules.WebHUD.manage import run_server

if __name__ == '__main__':
    print("Starting server")
    run_server()

