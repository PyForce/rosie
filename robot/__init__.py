#### IMPORT ####

#---- rOSi import ----
from robot import controller as Controller
from robot.planner import planner

#### GLOBAL VARIABLES ####

PATH_METHOD="Lineal Smooth"
            # "Cubic"
            # None

#### CLASS ####

class Master:
    def __init__(self):
        self.controller = Controller.Controller()
    
    #==== PRIVATE FUNCTIONS ====

    def _track_switcher(self, track):
        """
        Path controller switcher.
        
        :param track: trace to follow
        :type track: dict
        """
        #---- Cubic ----
        if PATH_METHOD == "Cubic":
            track['z_planning'] = track['t_planning']   
            track['constant_t'] = 10
            track['constant_k'] = 5
            track['cubic'] = True
        #---- Lineal Smooth ----        
        elif PATH_METHOD == "Lineal Smooth":
            if self.controller.finished:
                self.controller.move(track)
            return
        #---- None ----
        if self.controller.finished:
            self.controller.move(track, False)
    
    def get_robot_pos(self):
        return (-self.controller.y_position,
                        self.controller.x_position,
                        self.controller.z_position)
    
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
            path=planner.path_xyt(self.get_robot_pos(),request[0])
        if path:
            self._track_switcher(path)
        else:
            self.controller.action_exec()
            
    def process_user_request(self, request):
        
        right, left = self.controller.async_speed(request[0], request[1])
        if right or left:
            encoder1, encoder2, _ = self.controller.get_state()
            self.controller.navigation(encoder1, encoder2)
            self.controller.set_speed(right, left)
    
    
    
