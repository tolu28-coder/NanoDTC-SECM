import serial
import time
from threading import Event, Thread
import serial.tools.list_ports

# each 2048 steps is 50 um
# given in microns
STEP = 2048/50 

class Messenger(object):

    def __init__(self):
        self.callback = self._notgiven

    def _notgiven(self):
        raise NotImplementedError("Callback is not given")

    def setup(self, callback):
        self.callback = callback

    def notify(self):
        self.callback()

    def notify_with_args(self, *args, **kwargs):
        self.callback(*args, **kwargs)
        


class Arduino(object):
    
    def __init__(self, baud_rate=9600):
        self._open(baud_rate)
        # position in microns
        self.x_pos = 0
        self.y_pos = 0
        self.z_pos = 0
        self.is_busy = Event()
        self.not_busy()
        self.motion_done_messenger = Messenger()
        
        
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
            
        
    def find_port(self):
        ports = list(serial.tools.list_ports.comports())
        print(ports)
        if not ports:
            raise Exception("No ports found")
        for port in ports:
            """
            if "ACM" in port.name:
                self.port = port.device
                print("Using " + self.port + " for Arduino port")
            """
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
        state = self.device.read(1)
        self.not_busy()
        print(state)
        return state
    
    def move_x(self, distance):
        #distance in microns less than 50 microns
        steps = int(abs(STEP*distance))
        direction =  int(distance > 0) # check if positive or negative
        print(direction)
        b1 = int(steps//256) # convert to 2 byte int
        b2 = int(steps%256) # convert to 2 byte int
        x = "x" +chr(direction) + chr(b2) +chr(b1) + chr(0) +chr(0) # create byte string
        x = bytes(x, "utf-8") # actually convert into bytes
        # can construct message byte by byte
        self.send_and_receive(x)
        self.motion_done_messenger.notify()
        
    
    def move_y(self, distance):
        #distance in microns less than 50 microns
        steps = int(abs(STEP*distance))
        direction =  int(distance > 0) # check if positive or negative
        b1 = steps//256 # convert to 2 byte int
        b2 = steps%256 # convert to 2 byte int
        y = "y" +chr(direction) + chr(b2) +chr(b1) + chr(0) +chr(0) # create byte string
        y = bytes(y, "utf-8") # actually convert into bytes
        # can construct message byte by byte
        self.send_and_receive(y)
        self.motion_done_messenger.notify()

    
    def move_z(self, distance):
        #distance in microns less than 50 microns
        steps = int(abs(STEP*distance))
        direction =  int(distance > 0) # check if positive or negative
        b1 = steps//256 # convert to 2 byte int
        b2 = steps%256 # convert to 2 byte int
        z = "z" +chr(direction) + chr(b2) +chr(b1) + chr(0) +chr(0) # create byte string
        z = bytes(z, "utf-8") # actually convert into bytes
        # can construct message byte by byte
        self.send_and_receive(z)
        self.motion_done_messenger.notify()

if __name__=="__main__":
    device = Arduino()
    x = "x" +chr(0) + chr(0) +chr(8) + chr(0) +chr(0) # create byte string
    x = bytes(x, "utf-8") # actually convert into bytes
    y = "y" +chr(1) + chr(0) +chr(8) + chr(0) +chr(0) # create byte string
    y = bytes(y, "utf-8") # actually convert into bytes
    #device._send(x)

    

