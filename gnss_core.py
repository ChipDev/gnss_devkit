#pygnssutils is great for parsing NTRIP data and communicating with the F9P while also being
#able to shuffle data in and out. Right now, it's the best out-of-the-box solution for parsing
#NTRIP data from PointPerfect, which is a huge data saver, while also being able to log data
#and send it to other programs (even gpsd, mainly to use cgps)

#This script heavily depends on the example scripts from pygnssutils, but adds a tie-in with
#configuration for PointPerfect and logging/kml/bluetooth. It's not to be used in a production
#enviornment, but rather a great kick-start for development.

from logging import getLogger
from queue import Empty, Queue
from sys import argv
from threading import Event
from time import sleep
from datetime import datetime
import simplekml
import os
import stat
from simplekml import Kml, Snippet, Types
import datetime

from dynaconf import Dynaconf

from gnssapp import GNSSSkeletonApp
from pygnssutils import (
    VERBOSITY_HIGH,
    VERBOSITY_DEBUG,
    VERBOSITY_MEDIUM,
    GNSSNTRIPClient,
    set_logging,
)

CONNECTED = 1
logger = getLogger("pygnssutils")

kml = None
trk = None
fol = None
doc = None

def log_raw(parsed_data):
    if hasattr(parsed_data, 'lat') and hasattr(parsed_data, 'lon'):
        location_data = ({
            'time': f"{parsed_data.year}-{parsed_data.month}-{parsed_data.day} {parsed_data.hour}:{parsed_data.min}:{parsed_data.second}",
            'lat': parsed_data.lat,
            'lon': parsed_data.lon,
            'alt_mm': parsed_data.hMSL,
            'hAcc': parsed_data.hAcc,
        })

        with open("location_data.txt", "a") as log_file:
            log_file.write(str(location_data) + "\n")
        
        print(f"Logged {str(location_data)}")

def log_kml(parsed_data):
    if not (hasattr(parsed_data, 'lat') and hasattr(parsed_data, 'lon')):
        return
    global kml, trk, fol, doc
    if kml is None:
        kml = simplekml.Kml(name="GPS Track", open=1)
        doc = kml.newdocument(name="GPS Device", snippet=Snippet(f"Created at {datetime.datetime.now().isoformat()}"))
        fol = kml.newfolder(name='Tracks')
        trk = fol.newgxtrack(name=f"GPS {datetime.datetime.now().isoformat()}")
    print(f"Recieved PARSED DATA {str(parsed_data)}")
    #All zeroes for subsecond accuracy; obviously better data can be collected in a prod environemnt
    trk.newwhen([f"{parsed_data.year}-{parsed_data.month:02d}-{parsed_data.day:02d}T{parsed_data.hour:02d}:{parsed_data.min:02d}:{parsed_data.second:02d}.000000"])
    trk.newgxcoord([(parsed_data.lat, parsed_data.lon, parsed_data.hMSL/1000)])
    

def write_to_gpsd(parsed_data, file):
    try:
        print(f"Sent data to {file}")
        #Writing byte data to the virtual serial port.
        file.write(parsed_data.serialize())
    except (IOError, OSError) as write_error:
        print(f"Error writing to {file}: {write_error}")


def main(**kwargs):
    # Load NTRIP username/password if necessary
    settings = Dynaconf(settings_files=['.secrets.toml'])
    print("Loaded .secrets.toml")
    STREAM_NTRIP = kwargs.get("stream_ntrip", False)
    LOGGING_TO_FILE = kwargs.get("log_raw_location", True)
    LOGGING_TO_KML = kwargs.get("log_kml", True)

    # Our GPSD socat, by if enabled, pipes VIRT0 -> VIRT1, gpsd reads VIRT1.
    ENABLE_GPSD_BRIDGE = kwargs.get("gpsd_enable_bridge", False)
    GPSD_VIRTUAL_PORT_IN = kwargs.get("gpsd_vport", "/dev/ttyVIRT0")

    # GNSS receiver serial port parameters
    SERIAL_PORT = kwargs.get("gps_device", "/dev/ttyACM0") 
    BAUDRATE = 115200
    TIMEOUT = 10
    
    # NTRIP corrections are en/disabled in settings.
    
    # NTRIP caster parameters, edit for your specific caster.
    # Default is PointPerfect, a u-blox service.
    # Contact sales@gateworks.com for free access for a month.
    
    # Load NTRIP username/password if necessary
    settings = Dynaconf(settings_files=['.secrets.toml'])
    IPPROT = settings.IPPROT
    NTRIP_SERVER = settings.NTRIP_SERVER 
    NTRIP_PORT = settings.NTRIP_PORT
    HTTPS = settings.HTTPS
    FLOWINFO = settings.FLOWINFO
    SCOPEID = settings.SCOPEID
    MOUNTPOINT = settings.MOUNTPOINT
    NTRIP_USER = settings.NTRIP_USER
    NTRIP_PASSWORD = settings.NTRIP_PASSWORD
    DATATYPE = settings.DATATYPE
    


    GGAMODE = settings.GGAMODE
    GGAINT = settings.GGAINT
    REFLAT = settings.REFLAT
    REFLON = settings.REFLON
    REFALT = settings.REFALT
    REFSEP = settings.REFSEP

    recv_queue = Queue()  # data from receiver placed on this queue
    send_queue = Queue()  # data to receiver placed on this queue
    stop_event = Event()

    set_logging(logger, VERBOSITY_HIGH)
    mylogger = getLogger("pygnssutils.rtk_example")
    
    try:
        mylogger.info(f"Raw location logging: {LOGGING_TO_FILE}")
        mylogger.info(f"NTRIP streaming: {STREAM_NTRIP}")
        mylogger.info(f"Starting GNSS reader/writer on {SERIAL_PORT} @ {BAUDRATE}...")
        gna = GNSSSkeletonApp(
            SERIAL_PORT,
            BAUDRATE,
            TIMEOUT,
            stopevent=stop_event,
            recvqueue=recv_queue,
            sendqueue=send_queue,
            enableubx=True,
            showstatus=True,
        )

        gna.run()
        sleep(2) #Waiting for receiver to output at least 1 nav solution
        
        print(f"Streaming NTRIP data: {STREAM_NTRIP}")
        if STREAM_NTRIP: 
            mylogger.info(f"Starting NTRIP client on ${NTRIP_SERVER}:{NTRIP_PORT}...")
            gnc = GNSSNTRIPClient(gna)
            streaming = gnc.run(
                ipprot=IPPROT,
                server=NTRIP_SERVER,
                port=NTRIP_PORT,
                https=HTTPS,
                flowinfo=FLOWINFO,
                scopeid=SCOPEID,
                mountpoint=MOUNTPOINT,
                ntripuser=NTRIP_USER,
                ntrippassword=NTRIP_PASSWORD,
                reflat=REFLAT, 
                reflon=REFLON,
                refalt=REFALT,
                refsep=REFSEP,
                ggamode=GGAMODE,
                ggainterval=GGAINT,
                datatype=DATATYPE,
                output=send_queue,  # send NTRIP data to receiver
            )
        #if sending data to serial device, check validity
        SENDING_SERIAL = ENABLE_GPSD_BRIDGE
        SERIAL_DEVICE = GPSD_VIRTUAL_PORT_IN

        if SENDING_SERIAL:
            try:
                file_exists = os.path.exists(SERIAL_DEVICE)
                character_device = stat.S_ISCHR(os.stat(SERIAL_DEVICE).st_mode)
                if not file_exists:
                    raise RuntimeError(f"File not found: {SERIAL_DEVICE}")
                if not character_device:
                    raise RuntimeError(f"File is not a character device: {SERIAL_DEVICE}")
                
                serial_port = open(SERIAL_DEVICE, 'wb', buffering=0)

            except (FileNotFoundError, PermissionError, OSError) as e:
                print(f"Error opening file: {e}")
                ENABLE_GPSD_BRIDGE = false
                SENDING_SERIAL = false
        
        stop_ntrip = (STREAM_NTRIP and not streaming)
        while (not stop_event.is_set()) and not stop_ntrip:
            #Run until stop signal received
            if recv_queue is not None:
                #consume any received GNSS data from the queue
                try:
                    while not recv_queue.empty():
                        (_, parsed_data) = recv_queue.get(False)
                        recv_queue.task_done()
                        #print(f"Recieved: {str(parsed_data)}")
                        #Log data
                        if(ENABLE_GPSD_BRIDGE):
                            write_to_gpsd(parsed_data, serial_port)
                        if(LOGGING_TO_FILE):
                            log_raw(parsed_data) 
                        if(LOGGING_TO_KML):
                            log_kml(parsed_data)

                except Empty:
                    pass
            sleep(1)
    except KeyboardInterrupt:
       if kml is not None:
           # Styling
           trk.stylemap.normalstyle.iconstyle.icon.href = 'http://earth.google.com/images/kml-icons/track-directional/track-0.png'
           trk.stylemap.normalstyle.linestyle.color = '99ffac59'
           trk.stylemap.normalstyle.linestyle.width = 6
           trk.stylemap.highlightstyle.iconstyle.icon.href = 'http://earth.google.com/images/kml-icons/track-directional/track-0.png'
           trk.stylemap.highlightstyle.iconstyle.scale = 1.2
           trk.stylemap.highlightstyle.linestyle.color = '99ffac59'
           trk.stylemap.highlightstyle.linestyle.width = 8
           kml.save("location_data.kml")
           mylogger.info("Saved kml file location_data.kml")
       stop_event.set()
       mylogger.info("Terminated by user")

if __name__ == "__main__":
    main(**dict(arg.split("=") for arg in argv[1:]))


            


