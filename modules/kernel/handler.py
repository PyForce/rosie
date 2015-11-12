from modules.kernel import kernel
from modules import ordex

command = ordex.Command()



def get_odometry():
    return kernel.MASTER.get_robot_pos()

def get_metadata():
    return ''

def get_sensor(name=''):
    return []
    

def set_position(X=0,Y=0,theta=0):
    kernel.MASTER.set_robot_pos(X,Y,theta)

def process_text(text=""):
    print('Processing text: %s' % text)
    cmd = command.extraction(text)
    if isinstance(cmd, ordex.base.Common_Commands):
        print(cmd.CMD)
        kernel.execute(cmd.CMD)
    elif isinstance(cmd, ordex.base.Urgent_Commands):
        pass
    else:
        print("ERROR")

def set_keys(keys=[]):
    kernel.KEYS=keys

def set_mode(mode=''):
    if mode=='manual':
        kernel.execute([],'USER')
    else:
        kernel.execute([])
        
def set_path(path=[]):
    cmd=[{'start': None, 'end': None},
         {'path': path},
         {'command':'stop'}]
    kernel.execute([cmd])
    
