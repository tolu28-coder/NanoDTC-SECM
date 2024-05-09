import serial
import time


class Arduino(object):
    
    def __init__(self, baud_rate=9600):
        self._open(baud_rate)
        # position in microns
        self.x_pos = 0
        self.y_pos = 0
        self.z_pos = 0
        
        
    def _open(self, baud_rate):
        self.find_port()
        try:
            self.device = serial.Serial('/dev/ttyACM0',  baud_rate, timeout = 0.1)
            
        except SerialException:
            try:
                self.device = serial.Serial('/dev/ttyACM1',  baud_rate, timeout = 0.1)
                except SerialException:
                    raise Exception("Arduino not found")
                
    
    def __del__(self):
        self.device.close()
        super().__del__()
            
        
    def find_port(self):
        self.port=None
    
    def _send(self, data):
        self.device.write(data)
    
    def send(self, data):
        if len(data) != 6:
            raise Exception("Data sending to arduino only has " + str(len(data)) + "  char not 6 char")
        self._send(data)
    
    def send_and_receive(self, data):
        self.device.write(data)
        while True:
            try:
              time.sleep(0.01)
              state = self.device.readline()
              return state
            except:
              pass
            time.sleep(0.1)
            
    
    def move_x(self,direction, distance):
        #distance in microns
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
        
            