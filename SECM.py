from MotionController import MotionController
from Arduino import Arduino
from Potentiostat import Potentiostat


class SECM(object):
    
    def __init__(self):
        self.arduino = Arduino()
        self.motion_controller = MotionController(self.arduino)
        self.potentiostat = Potentiostat()