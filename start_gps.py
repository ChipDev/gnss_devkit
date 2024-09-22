#!/usr/bin/env python3

import subprocess
import signal
import sys
import os
import time

#Import configuration
from dynaconf import Dynaconf

# Load configuration
settings = Dynaconf(settings_files=['settings.toml'])

# Global flag to indicate when to stop
should_run = True

def signal_handler(signum, frame):
    global should_run
    should_run = False

def run_processes():
    global should_run
    processes = []
    try:
        #GPSD bridge: creates the socat serial ports, which allow us to talk to gpsd and therefore cgps.
        if(settings.gpsd_enable_bridge):

            # Ensures the logs directory exists
            os.makedirs('./logs', exist_ok=True)

            gpsd_stdout = open('./logs/gpsd_stdout', 'w')
            gpsd_stderr = open('./logs/gpsd_stderr', 'w')
            socat_stdout = open('./logs/socat_stdout', 'w')
            socat_stderr = open('./logs/socat_stderr', 'w')
            
            #The commands can be changed in settings.toml
            gpsd = subprocess.Popen(settings.gpsd_command.split(), stdout=gpsd_stdout, stderr=gpsd_stderr)
            socat = subprocess.Popen(settings.gpsd_socat_command.split(), stdout=socat_stdout, stderr=socat_stderr)
            processes.append(gpsd)
            processes.append(socat)

            print(f"Started gpsd (PID: {gpsd.pid}) and socat (PID: {socat.pid})")

        #Run main pygnssutils core program which takes in/distributes data.

        gpsd_virtual_port_in = settings.gpsd_virtual_port_in
        pygnssutils_cmd = f"python gnss_core.py stream_ntrip={settings.stream_ntrip} log_raw_location={settings.logging_type.raw_location} log_kml={settings.logging_type.kml} gpsd_enable_bridge={settings.gpsd_enable_bridge} gpsd_vport={gpsd_virtual_port_in} gps_device={settings.gps_device}"
        
        if not(settings.run_pygnssutils_in_foreground):
            #run pygnssutils in background
            print(f"Running pygnssutils gps core: {pygnssutils_cmd}")
            pygnsscore = subprocess.Popen(pygnssutils_cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            processes.append(pygnsscore)

            print(f"Running {settings.foreground_process} in the foreground. Press 'q' to quit.")
            foreground_process = subprocess.Popen(settings.foreground_process.split())
            processes.append(foreground_process)
        else:
            #pygnssutils runs in the foreground
            print(f"Running pygnssutils gps core: {pygnssutils_cmd}")
            foreground_process = subprocess.Popen(pygnssutils_cmd.split()) 
            processes.append(foreground_process)


        while should_run:
            time.sleep(1)
            if(settings.gpsd_enable_bridge):
                # Check if processes are still running
                if gpsd.poll() is not None or socat.poll() is not None:
                    print("One of the processes has terminated. Shutting down.")
                    should_run = False

    finally:
        print("Terminating processes...")
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
                proc.wait()
        print("All processes terminated.")

def main():
    
    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    run_processes()

if __name__ == "__main__":
    main()
