# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 12:48:42 2024

@author: tmna2
"""
import pspython.pspyinstruments as pspyinstruments
import pspython.pspymethods as pspymethods


def new_data_callback(new_data):
    for type, value in new_data.items():
        print(type + ' = ' + str(value))
    return



class Palmsens(object):
    
    def __init__(self):
        self.manager = pspyinstruments.InstrumentManager(new_data_callback=new_data_callback)
        available_instruments = self.manager.discover_instruments()
        print('connecting to ' + available_instruments[0].name)
        success = self.manager.connect(available_instruments[0])
        if success == 1:
            print('connection established')
        else:
            raise Exception("Palmsens potentiostat not connected")
        
    
    def measure_current(self):
        pass
    
    def CV_measurement(self):
        pass
    
    def chronoamperometry(self, interval_time=0.1, e=1, run_time=1, equilibration_time=1.0):
        method = pspymethods.chronoamperometry(interval_time=interval_time, e=e, run_time=run_time, equilibration_time=1)
        measurement = self.manager.measure(method)
        current = measurement.current_arrays
        voltage = measurement.potential_arrays
        return current, voltage
    

if __name__ == "__main__":
    potentiostat = Palmsens()
    print(potentiostat.chronoamperometry())