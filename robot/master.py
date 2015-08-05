######### IMPORT ##########

try: 
    import queue
except: 
    import Queue as queue

from robot import controller
from robot.planner import planner

########### GLOBAL VARIABLES ########### 
PATH_METHOD="Lineal Smooth"
#PATH_METHOD="Cubic"
#PATH_METHOD=None


class Master:
    def __init__(self):
        self.motion = controller.Controller()
        self.queue = queue.Queue()
        self.address = None
        self.index = 0
        self.ROBOT_POS = (0,0)

    #==== CUBIC ====
    def process_path(self, track):
        track['z_planning'] = track['t_planning']   
        track['constant_t'] = 10
        track['constant_k'] = 5
        track['cubic'] = True
        if self.motion.finished:
            self.motion.experiment_init(None, False, track)

    #==== OTHER ====
    def process_points(self, track):
        if self.motion.finished:
            self.motion.experiment_init(None, False, track)

    #==== LINEAL SMOOTH ====
    def process_reference(self, track):
        if self.motion.finished:
            self.motion.experiment_init(None, True, track)
    
    ######### MASTER FUNCTIONS #########
    
    def get_robot_pos(self):
        self.ROBOT_POS=(-self.motion.y_position,
                        self.motion.x_position)
#        return (self.motion.y_position,
#                self.motion.x_position,
#                self.motion.z_position)

    def is_finished(self):
        self.get_robot_pos()
        return self.motion.finished
        
    def end_task(self):
        self.motion.experiment_finish()

    def process_request(self, request):
        
        #---- set robot-action ----        
        #self.motion.action=request[1]
        self.motion.action='stop'
        
        #---- go to (place) ----
        path={}
        if request[0]:
            path=planner.path_xyt(self.ROBOT_POS,request[0])
        if path:
            if PATH_METHOD == "Lineal Smooth":
                self.process_reference(path)
            elif PATH_METHOD == "Cubic":
                self.process_path(path)
            else:
                self.process_points(path)
        else:
            self.motion.execute_action()
