######### IMPORT ##########

try: 
    import queue
except: 
    import Queue as queue

from robot import controller as Controller
from robot.planner import planner

########### GLOBAL VARIABLES ########### 
PATH_METHOD="Lineal Smooth"
#PATH_METHOD="Cubic"
#PATH_METHOD=None


class Master:
    def __init__(self):
        self.controller = Controller.Controller()
        self.queue = queue.Queue()
        self.address = None
        self.index = 0
        self.ROBOT_POS = (0,0,0)

    #==== CUBIC ====
    def process_path(self, track):
        track['z_planning'] = track['t_planning']   
        track['constant_t'] = 10
        track['constant_k'] = 5
        track['cubic'] = True
        if self.controller.finished:
            self.controller.move(track, False)

    #==== OTHER ====
    def process_points(self, track):
        if self.controller.finished:
            self.controller.move(track, False)

    #==== LINEAL SMOOTH ====
    def process_reference(self, track):
        if self.controller.finished:
            self.controller.move(track)
    
    ######### MASTER FUNCTIONS #########
    
    def get_robot_pos(self):
        self.ROBOT_POS=(-self.controller.y_position,
                        self.controller.x_position,
                        self.controller.z_position)
        return self.ROBOT_POS
    
    def set_robot_pos(self,X,Y,theta):
        self.controller.y_position=-X
        self.controller.x_position=Y
        self.controller.z_position=theta 

    def is_finished(self):
        self.get_robot_pos()
        return self.controller.finished
        
    def end_task(self):
        self.controller.end_move()

    def process_request(self, request):
        
        #---- set robot-action ----        
        #self.controller.action=request[1]
        self.controller.action='stop'
        
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
            self.controller.action_exec()
            
    def process_user_request(self, request):
        
        right, left = self.controller.async_speed(request[0], request[1])
        if right or left:
            encoder1, encoder2, _ = self.controller.get_state()
            self.controller.navigation(encoder1, encoder2)
            self.controller.set_speed(right, left)
    
    
    
