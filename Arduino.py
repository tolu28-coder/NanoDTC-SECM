import serial
import time
from threading import Event, Thread

# each 2048 steps is 50 um
# given in microns
STEP = 2048/50 

class Arduino(object):
    
    def __init__(self, baud_rate=9600):
        self._open(baud_rate)
        # position in microns
        self.x_pos = 0
        self.y_pos = 0
        self.z_pos = 0
        self.is_busy = Event()
        self.not_busy()
        
        
    def _open(self, baud_rate):
        self.find_port()
        try:
            self.device = serial.Serial('/dev/ttyACM0',  baud_rate, timeout = 0.1)
            
        except serial.SerialException:
            try:
                self.device = serial.Serial('/dev/ttyACM1',  baud_rate, timeout = 0.1)
            except serial.SerialException:
                raise Exception("Arduino not found")
    
    def check_busy(self):
        return self.is_busy.is_set()
    
    def set_busy(self):
        self.is_busy.set()
        
        
    def not_busy(self):
        self.is_busy.clear()
    
    def __del__(self):
        self.device.close()
        super().__del__()
            
        
    def find_port(self):
        self.port=None
    
    # _send should not be called as it does no checks if device is busy go through send method
    def _send(self, data):
        self.device.write(data)
    
    def send(self, data):
        if len(data) != 6:
            raise Exception("Data sending to arduino only has " + str(len(data)) + "  char not 6 char")
        while self.check_busy():
            time.sleep(0.1)
        self.set_busy()
        self._send(data)
    
    def send_and_receive(self, data):
        self.send(data)
        while True:
            try:
              time.sleep(0.01)
              state = self.device.readline()
              self.not_busy()
              return state
            except:
              pass
            time.sleep(0.1)
    
    def move_x(self,direction, distance):
        #distance in microns less than 50 microns
        steps = int(STEP*distance)
        direction =  int(steps > 0) # check if positive or negative
        steps
        
        pass
    
    def move_y(self,direction, distance):
        #distance in microns
        pass

    
    def move_z(self,direction, distance):
        #distance in microns
        pass
    
    def move_to_x(self, x):
        pass
    
    def move_to_y(self, y):
        pass
    
    def move_to_z(self, z):
        pass
    
    def move_to(x, y, z):
        if x != self.x_pos:
            self.move_to_x(x)
        if y != self.y_pos:
            pass
        if z != self.z_pos:
            pass
        
            