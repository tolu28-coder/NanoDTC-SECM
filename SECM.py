from MotionController import MotionController
from Arduino import Arduino
#from Potentiostat import Potentiostat
import numpy as np
import time
#from Palmsens_potentiostat import Palmsens


class SECM(object):
    
    def __init__(self):
        self.arduino = Arduino()
        self.motion_controller = MotionController(self.arduino)
        #self.potentiostat = Potentiostat()
        #self.potentiostat = Palmsens()
    
    def current_scan(self, voltage, x_range, y_range, steps, file):
        data = np.zeros([steps, steps])
        index, instruction = self.motion_controller.generate_xy_image_scan(x_range, y_range, steps)
        for i in range(len(index)):
            data[index[i]] = self.measure_current(voltage)
            tmp = instruction[i]
            print(tmp)
            self.motion_controller.move(tmp[0], tmp[1], tmp[2])
        np.savetxt(file, data)


    def approach_curve(self):
        pass
    
    
    def approach_curve_scan(self, voltage, z_range, steps, order="Ascending", file="test.txt"):
        data = []
        if order == "Ascending":    
            instructions = self.motion_controller.get_approach_curve(z_range, steps)
            z = np.linspace(0,z_range, steps)
        elif order == "Descending":    
            instructions = self.motion_controller.get_negative_approach_curve(z_range, steps)
            z = np.linspace(-z_range,0, steps)
        for i in instructions:
            data.append(self.measure_current(voltage))
            self.motion_controller.move(i)
        data = np.array(data)
        to_save = np.array([z, data])
        np.savetxt(file, to_save)
        
        
        

    def measure_current(self, voltage):
        current, v = self.chronoamperometry(e = voltage)
        return sum(current)/len(current)

    
    def chronoamperometry(self, interval_time=0.1, e=1, run_time=1, equilibration_time=1.0):
        return self.potentiostat.chronoamperometry(interval_time=0.1, e=1, run_time=1, equilibration_time=1.0)
    
    def set_voltage(self, v):
        pass
        
if __name__ == "__main__":
    device = SECM()
    print(device.motion_controller)
        