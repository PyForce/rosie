"""
DEFINED ACTIONS FOR THE MOBILE ROBOT

This script sholud be programed for the user as part of Controller class.
"""

#==== ROTATE ====
if self.action=='turn':
    self.action='stop'
    angle=self.request['value']
    angle=math.pi*angle/180.0 + self.z_position-int(self.z_position/(2*math.pi))*2*math.pi

    self.rotate(angle)

#==== STOP ====
elif self.action=='stop':
    self.set_speed()
    self.end_move()
