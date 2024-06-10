from MotionController import MotionController
from Arduino import Arduino
from Potentiostat import Potentiostat
import numpy as np


class SECM(object):
    
    def __init__(self):
        self.arduino = Arduino()
        self.motion_controller = MotionController(self.arduino)
        #self.potentiostat = Potentiostat()
    
    def current_scan(self, x_range, y_range, steps, file):
        data = np.zeros([steps, steps])
        index, instruction = self.motion_controller.generate_xy_image_scan(x_range, y_range, steps)
        for i in range(len(index)):
            data[index[i]] = self.measure_current()
            self.motion_controller.move(instruction[i][0], instruction[i][1], instruction[i][2])
        np.savetxt(file, data)

    def measure_current(self, to_average=5):
        buf = []
        for i in range(to_average):
            buf.append(self.current)
        return sum(buf)/to_average
    
    @property
    def current(self):
        return self.potentiostat.measure_current()
    
    def set_voltage(self, v):
        pass
        
if __name__ == "__main__":
    device = SECM()
    print(device.motion_controller)
        