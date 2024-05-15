import sys, platform
import time, datetime, timeit
import usb.core, usb.util
import os.path
import collections
import numpy as np
import scipy.integrate


class AverageBuffer:
    """Collect samples and compute an average as soon as a sufficient number of samples is added."""
    def __init__(self, number_of_samples_to_average):
        self.number_of_samples_to_average = number_of_samples_to_average
        self.samples = []
        self.averagebuffer = []
    
    def add_sample(self, sample):
        self.samples.append(sample)
        if len(self.samples) >= self.number_of_samples_to_average:
            self.averagebuffer.append(sum(self.samples)/len(self.samples))
            self.samples = []
            
    def clear(self):
        self.samples = []
        self.averagebuffer = []

class States():
    """Expose a named list of states to be used as a simple state machine."""
    # Used as a sort of Enum
    NotConnected, Idle_Init, Idle, Measuring_Offset, Stationary_Graph, Measuring_CV, Measuring_CD, Measuring_Rate = range(8)
    
state = States.NotConnected # Initial state

class Potentiostat(object):
    # Ultilising the Mystat potentiostat and code (DOI:https://doi.org/10.1016/j.ohx.2020.e00163)
    # Only works on linux (Raspberry pi)
    
    def __init__(self):
        self.usb_vid = "0xa0a0" # Default USB vendor ID, can also be adjusted in the GUI
        self.usb_pid = "0x0002" # Default USB product ID, can also be adjusted in the GUI
        self.current_range_list = ["200 mA", u"20 mA", u"200 µA", u"2 µA"]
        self.shunt_calibration = [1.,1.,1.,1.] # Fine adjustment for shunt resistors, containing values of R1/1ohm, R2/10ohm, R3/1kohm, R4/100kohm (can also be adjusted in the GUI)
        self.currentrange = 0 # Default current range (expressed as index in current_range_list)
        self.units_list = ["Potential (V)", "Current (mA)", "DAC Code"]
        self.dev = None # Global object which is reserved for the USB device
        self.current_offset = 0. # Current offset in DAC counts
        self.potential_offset = 0. # Potential offset in DAC counts
        self.potential = 0. # Measured potential in V
        self.current = 0. # Measured current in mA
        self.last_potential_values = collections.deque(maxlen=200)
        self.last_current_values = collections.deque(maxlen=200)
        self.raw_potential = 0 # Measured potential in ADC counts
        self.raw_current = 0 # Measured current in ADC counts
        self.last_raw_potential_values = collections.deque(maxlen=200)
        self.last_raw_current_values = collections.deque(maxlen=200)
        self.cv_parameters = {} # Dictionary to hold the CV parameters
        self.cd_parameters = {} # Dictionary to hold the charge/discharge parameters
        self.rate_parameters = {} # Dictionary to hold the rate testing parameters
        self.overcounter, undercounter, skipcounter = 0, 0, 0 # Global counters used for automatic current ranging
        self.time_of_last_adcread = 0.
        self.adcread_interval = 0.09 # ADC sampling interval (in seconds)
        self.logging_enabled = False # Enable logging of potential and current in idle mode (can be adjusted in the GUI)
        self.busyloop_interval = adcread_interval
        self.qt_timer_period = 0
        self.state = States.NotConnected # Initial state
    
    def take_CV(self):
        pass
    
    def measure_current(self):
        pass
    
    def send_command(self, command_string, expected_response, log_msg=None):
        """Send a command string to the USB device and check the response; optionally logs a message to the message log."""
        if self.dev is not None: # Make sure it's connected
            self.dev.write(0x01,command_string) # 0x01 = write address of EP1
            response = bytes(self.dev.read(0x81,64)) # 0x81 = read address of EP1
            if response != expected_response:
                QtGui.QMessageBox.critical(mainwidget, "Unexpected Response", "The command \"%s\" resulted in an unexpected response. The expected response was \"%s\"; the actual response was \"%s\""%(command_string,expected_response.decode("ascii"),response.decode("ascii")))
            else:
                if log_msg != None:
                    self.log_message(log_msg)
            return True
        else:
            self.not_connected_errormessage()
            return False
    
    
    def not_connected_errormessage(self):
        """Generate an error message stating that the device is not connected."""
        QtGui.QMessageBox.critical(mainwidget, "Not connected", "This command cannot be executed because the USB device is not connected. Press the \"Connect\" button and try again.")
    
    def check_state(self, desired_states):
        """Check if the current state is in a given list. If so, return True; otherwise, show an error message and return False."""
        if self.state not in desired_states:
            if self.state == 0:
                self.not_connected_errormessage()
            else:
                QtGui.QMessageBox.critical(mainwidget, "Error", "This command cannot be executed in the current state.")
            return False
        else:
            return True
        
        
    def set_cell_status(self, cell_on_boolean):
        """Switch the cell connection (True = cell on, False = cell off)."""
        if cell_on_boolean:
            if self.send_command(b'CELL ON', b'OK'):
                cell_status_monitor.setText("CELL ON")
        else:
            if self.send_command(b'CELL OFF', b'OK'):
                cell_status_monitor.setText("CELL OFF")


    def set_control_mode(self, galvanostatic_boolean):
        """Switch the control mode (True = galvanostatic, False = potentiostatic)."""
        if galvanostatic_boolean:
            if self.send_command(b'GALVANOSTATIC', b'OK'):
                control_mode_monitor.setText("GALVANOSTATIC")
        else:
            if self.send_command(b'POTENTIOSTATIC', b'OK'):
                control_mode_monitor.setText("POTENTIOSTATIC")

    def set_current_range(self):
        """Switch the current range based on the GUI dropdown selection."""
        index = hardware_manual_control_range_dropdown.currentIndex()
        commandstring = [b'RANGE 1',b'RANGE 2',b'RANGE 3',b'RANGE 4'][index]
        if self.send_command(commandstring, b'OK'):
            current_range_monitor.setText(current_range_list[index])
            self.currentrange = index

    def auto_current_range(self):
        """Automatically switch the current range based on the measured current; returns a number of measurements to skip (to suppress artifacts)."""
        if self.currentrange == 0:
            relativecurrent = abs(self.current/(2000.))
        elif self.currentrange == 1:
            relativecurrent = abs(self.current/(20.))
        elif self.currentrange == 2:
            relativecurrent = abs(self.current/(0.2))
        elif self.currentrange == 3:
            relativecurrent = abs(self.current/(0.002))
        if relativecurrent > 1.05 and self.currentrange != 0 and cv_range_checkboxes[currentrange-1].isChecked(): # Switch to higher current range (if possible) after three detections
            self.overcounter += 1
        else:
            self.overcounter = 0
        if relativecurrent < 0.0095 and self.currentrange != 3 and cv_range_checkboxes[currentrange+1].isChecked(): # Switch to lower current range (if possible) after three detections
            self.undercounter += 1
        else:
            self.undercounter = 0
        if self.overcounter > 3:
            self.currentrange -= 1
            hardware_manual_control_range_dropdown.setCurrentIndex(currentrange)
            self.set_current_range()
            self.overcounter = 0
            return 2 # Skip next two measurements to suppress artifacts
        elif self.undercounter > 3:
            self.currentrange += 1
            hardware_manual_control_range_dropdown.setCurrentIndex(currentrange)
            self.set_current_range()
            self.undercounter = 0
            return 2 # Skip next two measurements to suppress artifacts
        else:
            return 0
    
    
    @staticmethod
    def current_range_from_current(current):
        """Return the current range that best corresponds to a given current."""
        current = abs(current)
        if current <= 0.002:
            return 3 # Lowest current range (2 uA)
        elif current <= 0.2:
            return 2 # Intermediate current range (200 uA)
        elif current <= 20.:
            return 1 # Intermediate current range (20 mA)
        else:
            return 0 # Highest current range (200 mA)

    @staticmethod
    def get_next_enabled_current_range(desired_currentrange):
        """Return an enabled current range that best corresponds to a desired current range."""
        range_found = False
        found_currentrange = desired_currentrange
        for i in range(desired_currentrange,-1,-1): # Look for an enabled current range, going up in current range
            if cv_range_checkboxes[i].isChecked():
                found_currentrange = i
                range_found = True
                break
        if not range_found:
            for i in range(desired_currentrange,4): # Look for an enabled current range, going down in current range
                if cv_range_checkboxes[i].isChecked():
                    found_currentrange = i
                    break
        return found_currentrange

    def set_offset(self):
        """Save offset values to the device's flash memory."""
        self.send_command(b'OFFSETSAVE '+self.decimal_to_dac_bytes(self.potential_offset)+self.decimal_to_dac_bytes(self.current_offset), b'OK', "Offset values saved to flash memory.")


    @staticmethod
    def twocomplement_to_decimal(msb, middlebyte, lsb):
        """Convert a 22-bit two-complement ADC value consisting of three bytes to a signed integer (see MCP3550 datasheet for details)."""
        ovh = (msb > 63) and (msb < 128) # Check for overflow high (B22 set)
        ovl = (msb > 127) # Check for overflow low (B23 set)
        combined_value = (msb%64)*2**16+middlebyte*2**8+lsb # Get rid of overflow bits
        if not ovh and not ovl:
            if msb > 31: # B21 set -> negative number
                answer = combined_value - 2**22
            else:
                answer = combined_value
        else: # overflow
            if msb > 127: # B23 set -> negative number
                answer = combined_value - 2**22
            else:
                answer = combined_value
        return answer
    
    @staticmethod
    def decimal_to_dac_bytes(value):
        """Convert a floating-point number, ranging from -2**19 to 2**19-1, to three data bytes in the proper format for the DAC1220."""
        code = 2**19 + int(round(value)) # Convert the (signed) input value to an unsigned 20-bit integer with zero at midway
        code = np.clip(code, 0, 2**20 - 1) # If the input exceeds the boundaries of the 20-bit integer, clip it
        byte1 = code // 2**12
        byte2 = (code % 2**12) // 2**4
        byte3 = (code - byte1*2**12 - byte2*2**4)*2**4
        return bytes([byte1,byte2,byte3])
    
    @staticmethod
    def dac_bytes_to_decimal(dac_bytes):
        """Convert three data bytes in the DAC1220 format to a 20-bit number ranging from -2**19 to 2**19-1."""
        code = 2**12*dac_bytes[0]+2**4*dac_bytes[1]+dac_bytes[2]/2**4
        return code - 2**19
    
    @staticmethod
    def float_to_twobytes(value):
        """Convert a floating-point number ranging from -2^15 to 2^15-1 to a 16-bit representation stored in two bytes."""
        code = 2**15 + int(round(value))
        code = np.clip(code, 0, 2**16 - 1) # If the code exceeds the boundaries of a 16-bit integer, clip it
        byte1 = code // 2**8
        byte2 = code % 2**8
        return bytes([byte1,byte2])

    @staticmethod
    def twobytes_to_float(bytes_in):
        """Convert two bytes to a number ranging from -2^15 to 2^15-1."""
        code = 2**8*bytes_in[0]+bytes_in[1]
        return float(code - 2**15)
    
    def get_offset(self):
        """Retrieve offset values from the device's flash memory."""
        global potential_offset, current_offset
        if self.dev is not None: # Make sure it's connected
            self.dev.write(0x01,b'OFFSETREAD') # 0x01 = write address of EP1
            response = bytes(self.dev.read(0x81,64)) # 0x81 = read address of EP1
            if response != bytes([255,255,255,255,255,255]): # If no offset value has been stored, all bits will be set
                self.potential_offset = dac_bytes_to_decimal(response[0:3])
                self.current_offset = dac_bytes_to_decimal(response[3:6])    
                hardware_calibration_potential_offset.setText("%d"%potential_offset)
                hardware_calibration_current_offset.setText("%d"%current_offset)    
                self.log_message("Offset values read from flash memory.")
            else:
                self.log_message("No offset values were found in flash memory.")
        else:
            self.not_connected_errormessage()
    
    def connect_disconnect_usb(self):
        """Toggle the USB device between connected and disconnected states."""
        if self.dev is not None: # If the device is already connected, then this function should disconnect it
            usb.util.dispose_resources(self.dev)
            self.dev = None
            state = States.NotConnected
            self.log_message("USB Interface disconnected.")
            return
        # Otherwise, try to connect
        self.dev = usb.core.find(idVendor=int(self.usb_vid, 0), idProduct=int(self.usb_pid, 0))
        if self.dev is None:
            #QtGui.QMessageBox.critical(mainwidget, "USB Device Not Found", "No USB device was found with VID %s and PID %s. Verify the vendor/product ID and check the USB connection."%(usb_vid_string,usb_pid_string))
            pass
        else:
            self.log_message("USB Interface connected.")
            try:
                #hardware_device_info_text.setText("Manufacturer: %s\nProduct: %s\nSerial #: %s"%(dev.manufacturer,dev.product,dev.serial_number))
                self.get_calibration()
                self.set_cell_status(False) # Cell off
                self.set_control_mode(False) # Potentiostatic control
                self.set_current_range() # Read current range from GUI
                self.state = States.Idle_Init # Start idle mode
            except ValueError:
                # handle device not calibrated
                pass # In case the device is not yet calibrated
    
    def log_message(self, data):
        pass
    
    def emergency_shutdown(self):
        '''Turns the cell off if the current is above 220 mA'''
        if np.absolute(self.current) > 220.:
            if self.state != States.Idle:
                preview_cancel_button.show()
                self.state = States.Idle
            set_control_mode(True)
            set_output(1,0.)
            QtGui.QMessageBox.critical(mainwidget, "Warning!","The current has exceeded its maximum value of 200 mA.")
            
    def wait_for_adcread(self):
        """Wait for the duration specified in the busyloop_interval."""
        if busyloop_interval == 0:
            return # On Linux/Mac, system timing is used instead of the busyloop
        else:
            time.sleep(busyloop_interval/2.) # Sleep for some time to prevent wasting too many CPU cycles
            app.processEvents() # Update the GUI
            while timeit.default_timer() < time_of_last_adcread + busyloop_interval:
                pass # Busy loop (this is the only way to get accurate timing on MS Windows)
    
    
    def offset_changed_callback(self):
        """Set the potential and current offset from the input fields."""
        global potential_offset, current_offset
        try:
            potential_offset = int(hardware_calibration_potential_offset.text())
            hardware_calibration_potential_offset.setStyleSheet("")
        except ValueError: # If the input field cannot be interpreted as a number, color it red
            hardware_calibration_potential_offset.setStyleSheet("QLineEdit { background: red; }")
        try:
            current_offset = int(hardware_calibration_current_offset.text())
            hardware_calibration_current_offset.setStyleSheet("")
        except ValueError: # If the input field cannot be interpreted as a number, color it red
            hardware_calibration_current_offset.setStyleSheet("QLineEdit { background: red; }")

    def shunt_calibration_changed_callback(self):
        """Set the shunt calibration values from the input fields."""
        for i in range(0,4):
            try:
                shunt_calibration[i] = float(hardware_calibration_shuntvalues[i].text())
                hardware_calibration_shuntvalues[i].setStyleSheet("")
            except ValueError: # If the input field cannot be interpreted as a number, color it red
                hardware_calibration_shuntvalues[i].setStyleSheet("QLineEdit { background: red; }")

    def set_dac_calibration(self):
        """Save DAC calibration values to the DAC and the device's flash memory."""
        try:
            self.dac_offset = int(hardware_calibration_dac_offset.text())
            hardware_calibration_dac_offset.setStyleSheet("")
        except ValueError: # If the input field cannot be interpreted as a number, color it red
            hardware_calibration_dac_offset.setStyleSheet("QLineEdit { background: red; }")
            return
        try:
            self.dac_gain = int(hardware_calibration_dac_gain.text())
            hardware_calibration_dac_gain.setStyleSheet("")
        except ValueError: # If the input field cannot be interpreted as a number, color it red
            hardware_calibration_dac_gain.setStyleSheet("QLineEdit { background: red; }")
            return
        self.send_command(b'DACCALSET '+decimal_to_dac_bytes(dac_offset)+decimal_to_dac_bytes(dac_gain-2**19), b'OK', "DAC calibration saved to flash memory.")

    def get_dac_calibration(self):
        """Retrieve DAC calibration values from the device's flash memory."""
        if dev is not None: # Make sure it's connected
            dev.write(0x01,b'DACCALGET') # 0x01 = write address of EP1
            response = bytes(dev.read(0x81,64)) # 0x81 = write address of EP1
            if response != bytes([255,255,255,255,255,255]): # If no calibration value has been stored, all bits are set
                dac_offset = dac_bytes_to_decimal(response[0:3])
                dac_gain = dac_bytes_to_decimal(response[3:6])+2**19
                hardware_calibration_dac_offset.setText("%d"%dac_offset)
                hardware_calibration_dac_gain.setText("%d"%dac_gain)
                log_message("DAC calibration read from flash memory.")
            else:
                log_message("No DAC calibration values were found in flash memory.")
        else:
            not_connected_errormessage()

    def set_calibration(self):
        """Save all calibration values to the device's flash memory."""
        self.set_dac_calibration()
        self.set_offset()
        self.set_shunt_calibration()

    def get_calibration(self):
        """Retrieve all calibration values from the device's flash memory."""
        self.get_dac_calibration()
        self.get_offset()
        self.get_shunt_calibration()

    def dac_calibrate(self):
        """Activate the automatic DAC1220 calibration function and retrieve the results."""
        self.send_command(b'DACCAL', b'OK', "DAC calibration performed.")
        self.get_dac_calibration()

    def set_output(self, value_units_index, value):
        """Output data to the DAC; units can be either V (index 0), mA (index 1), or raw counts (index 2)."""
        if value_units_index == 0:
            self.send_command(b'DACSET '+self.decimal_to_dac_bytes(value/13.4*2.**19+int(round(self.potential_offset/4.))), b'OK')
        elif value_units_index == 1:
            if self.currentrange == 0:
                self.send_command(b'DACSET '+self.decimal_to_dac_bytes(value/(250./self.shunt_calibration[self.currentrange])*2.**19+int(round(self.current_offset/4.))), b'OK')
            if self.currentrange == 1:
                self.send_command(b'DACSET '+self.decimal_to_dac_bytes(value/(25./self.shunt_calibration[self.currentrange])*2.**19+int(round(self.current_offset/4.))), b'OK')
            if self.currentrange == 2:
                self.send_command(b'DACSET '+self.decimal_to_dac_bytes(value/(0.25/self.shunt_calibration[self.currentrange])*2.**19+int(round(self.current_offset/4.))), b'OK')
            if self.currentrange == 3:
                self.send_command(b'DACSET '+self.decimal_to_dac_bytes(value/(0.0025/self.shunt_calibration[self.currentrange])*2.**19+int(round(self.current_offset/4.))), b'OK')
        elif value_units_index == 2:
            self.send_command(b'DACSET '+self.decimal_to_dac_bytes(value), b'OK')

    def wait_for_adcread(self):
        """Wait for the duration specified in the busyloop_interval."""
        if self.busyloop_interval == 0:
            return # On Linux/Mac, system timing is used instead of the busyloop
        else:
            time.sleep(busyloop_interval/2.) # Sleep for some time to prevent wasting too many CPU cycles
            app.processEvents() # Update the GUI
            while timeit.default_timer() < time_of_last_adcread + busyloop_interval:
                pass # Busy loop (this is the only way to get accurate timing on MS Windows)

    def read_potential_current(self):
        """Read the most recent potential and current values from the device's ADC."""
        
        self.wait_for_adcread()
        self.time_of_last_adcread = timeit.default_timer()
        self.dev.write(0x01,b'ADCREAD') # 0x01 = write address of EP1
        response = bytes(self.dev.read(0x81,64)) # 0x81 = read address of EP1
        if response != b'WAIT': # 'WAIT' is received if a conversion has not yet finished
            raw_potential = self.twocomplement_to_decimal(response[0], response[1], response[2])
            raw_current = self.twocomplement_to_decimal(response[3], response[4], response[5])
            potential = (raw_potential-self.potential_offset)/2097152.*13.4 # Calculate potential in V, compensating for offset
            if self.currentrange == 0:# Calculate current in mA, taking current range into account and compensating for offset
                current = (raw_current-self.current_offset)/2097152.*250./(self.shunt_calibration[self.currentrange])
            elif self.currentrange == 1:
                current = (raw_current-self.current_offset)/2097152.*25./(self.shunt_calibration[self.currentrange])
            elif self.currentrange == 2:
                current = (raw_current-self.current_offset)/2097152.*0.25/(self.shunt_calibration[self.currentrange])
            elif self.currentrange == 3:
                current = (raw_current-self.current_offset)/2097152.*0.0025/(self.shunt_calibration[self.currentrange])
            #potential_monitor.setText(potential_to_string(potential))
            #current_monitor.setText(current_to_string(currentrange, current))
            if self.logging_enabled: # If enabled, all measurements are appended to an output file (even in idle mode)
                try:
                    print("%.2f\t%e\t%e"%(time_of_last_adcread,potential,current*1e-3),file=open(hardware_log_filename.text(),'a',1)) # Output tab-separated data containing time (in s), potential (in V), and current (in A)
                except:
                    QtGui.QMessageBox.critical(mainwidget, "Logging error!", "Logging error!")
                    hardware_log_checkbox.setChecked(False) # Disable logging in case of file errors
    
    
    