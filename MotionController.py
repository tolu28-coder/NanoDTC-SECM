from threading import Event, Thread
import time


class MotionController(object):
    
    
    def __init__(self, arduino):
        self.arduino = arduino
        self.is_busy = Event()
        self.not_busy()
        self.arduino.motion_done_messenger.setup(self.not_busy)
        
    
    
    def check_busy(self):
        return self.is_busy.is_set()
    
    def set_busy(self):
        self.is_busy.set()
        
        
    def not_busy(self):
        self.is_busy.clear()
        
        
        
    def generate_xy_image_scan(self, x_range, y_range, steps):
        x_steps = x_range // steps
        y_steps = y_range // steps
        instruction = []
        index = []
        direction = 0
        for i in range(steps):
            for j in range(steps-1):
                if direction == 0:
                    instruction.append([0, y_steps, 0])
                    index.append([i,j])
                elif direction == 1:
                    instruction.append([0, -y_steps, 0])
                    index.append([i,steps - j-1])
            if direction == 0:
                index.append([i, steps-1])
            else:
                index.append([i, 0]) 
            if direction == 1:
                direction = 0
            else :
                direction = 1
            instruction.append([x_steps,0,0])
        return index, instruction
            
                
    def get_approach_curve(self, z_range, steps):
        z_steps = z_range//steps
        instruction = [[0,0,z_steps]]*steps
        return instruction
    
    def get_negative_approach_curve(self, z_range, steps):
        z_steps = z_range//steps
        instruction = [[0,0,-z_steps]]*steps
        return instruction
    
    def move(self, x, y, z):
        if x:
            self.move_x(x)
        if y:
            self.move_y(y)
        if z:
            self.move_z(z)

    def move_x(self, x):
        self.arduino.move_x(x)
        

    def move_y(self, y):
        self.arduino.move_y(y)


    def move_z(self, z):
        self.arduino.move_z(z)
    
    
    
        
    