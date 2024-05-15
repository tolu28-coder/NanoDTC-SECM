import serial
import time
from threading import Event, Thread
import serial.tools.list_ports

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
            self.device = serial.Serial(self.port,  baud_rate, timeout = 0.1)
            
        except serial.SerialException:
            raise Exception("Unable to connect")
    
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
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            raise Exception("No ports found")
        for port in ports:
            if "ACM" in port.name:
                self.port = port.device
                print("Using " + self.port + " for Arduino port")
                break
    
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
        while not self.device.in_waiting:
            time.sleep(0.1)
        state = self.device.readline()
        self.not_busy()
        print(state)
        return state
    
    def move_x(self,direction, distance):
        #distance in microns less than 50 microns
        steps = int(STEP*distance)
        direction =  int(steps > 0) # check if positive or negative
        b1 = steps//256 # convert to 2 byte int
        b2 = steps%256 # convert to 2 byte int
        x = "x" +chr(direction) + chr(b2) +chr(b1) + chr(0) +chr(0) # create byte string
        x = bytes(x, "utf-8") # actually convert into bytes
        # can construct message byte by byte
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
    
    def move_to(self, x, y, z):
        if x != self.x_pos:
            self.move_to_x(x)
        if y != self.y_pos:
            pass
        if z != self.z_pos:
            pass


