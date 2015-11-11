
print('Importing module: ordex...')
try:
    from modules import ordex
    print('ordex... Ok')
except Exception as e:
    print(e)
    print('ordex... Fail')


print('Importing module: kernel...')
try:
    from modules.kernel import kernel
    print('kernel... Ok')
except Exception as e:
    print(e)
    print('kernel... Fail')

command = ordex.Command()
command.draw_syntactic_trees(False)

