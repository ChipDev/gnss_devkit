```                                                                                                   
  ██████   █████  ████████ ███████ ██     ██  ██████  ██████  ██   ██ ███████ 
 ██       ██   ██    ██    ██      ██     ██ ██    ██ ██   ██ ██  ██  ██      
 ██   ███ ███████    ██    █████   ██  █  ██ ██    ██ ██████  █████   ███████ 
 ██    ██ ██   ██    ██    ██      ██ ███ ██ ██    ██ ██   ██ ██  ██       ██ 
  ██████  ██   ██    ██    ███████  ███ ███   ██████  ██   ██ ██   ██ ███████ 
```                                                                             
               Welcome to the Gateworks GNSS Development Kit!


The Venice GW7200 is a state-of-the-art industrial SBC
from the Venice line. This development kit includes:

    HARDWARE:
    1.   GW7200  Industrial SBC + SoC
    2.  GW16143  High Precision GNSS/GPS card
    3.  GW16132  CAT M1 Cellular & BLE Radio card
    4.  GW16100  u-blox L1/L2 Band, Precision GNSS Antenna
    5.  GW10030  AC/DC 24V 1A Power Supply
    6.  GW16099  JTAG USB Programmer/Serial
    7.  GW10018  2x CAT5 Ethernet
    8.  GW10045  USB Type A Male->Female
    9.  GW10074  MMCX to SMA Female Cable
    10. GW10043  BLE Antenna + GW10035 Antenna Cable
    11. GW16065  Celluar Antenna + GW10036 Antenna Cable
    12. GW17045  Hologram SIM for celluar.

             
    SOFTWARE:
    1. We set you up with Ubuntu. For specifics, use $ uname -a 
    2. Setup and example scripts for celluar & GPS. See below.
    3. Necessary kernel drivers for robust operation.

With these components, the applications are endless.
Industry-grade, rugged hardware allows your solution to be
deployed to new environments with confidence. 

We provide support for each of the products, i.e. the GW16143
on our Wiki at trac.gateworks.com, along with loads of other useful
information and scripts.

---------------------------------------------------------------------------------------------------
 
                     GPS TESTING SCRIPT: start_gps.py
                      What can it do out of the box?                       


    ┌───────────────────────┐
    │                       │
    │  GPS Device GW16143   │
    │     /dev/ttyACM0      │ ──────┐                         ┌─────────────┐
    │                       │       ▼                         │             │
    │     Location Info     │    ┌─────────────────────┐      │   Logging   │
    │                       │    │                     │      │  Raw & KML  │        ┌───────────────────┐
    └───────────────────────┘    │                     │ ───► │ --> Google  │        │                   │
                                 │     PyGNSSUtils     │      │    Earth    │        │    GPSD / cgps    │
                                 │  Core data handler  │      └─────────────┘        │                   │
    ┌───────────────────────┐    │                     │                             │    Visualizer     │
    │                       │    │                     │    ┌─────────────────┐      │ OPTIONAL standard │
    │     PointPerfect      │    └─────────────────────┘    │                 │ ───► │ Linux GNSS Client │
    │    < 2cm GNSS fix     │       ▲                       │      Socat      │      │                   │
    │                       ├───────┘               │       │                 │      └───────────────────┘
    │                       │                       └────►  │ VIRT0 --> VIRT1 │
    └───────────────────────┘                               │     Virtual     │      ┌───────────────────┐
                                                            │   serial port   │      │                   │
                                                            │                 │      │     u-center      │
                                                            └─────────────────┘      │  u-blox gps tool  │
                                                                                     │   Windows ONLY    │
                                                                                     │  Configuration &  │
                                                                                     │   Visualization   │
                                                                                     │                   │
                                                                                     └───────────────────┘


The only required components are: The GPS device connected to the GW16143 and PyGNSSUtils. 
All other parts, such as PointPerfect can be enabled/disabled in settings.toml.
PointPerfect credentials are configured in .settings.toml (note the .)
Included in your DevKit is a celluar SIM card from Hologram. See the wiki for setup.
Once configured, the internet can be accessed normally and all scripts should function.

----------------------------------------------------------------------------------------------------

USAGE: Download dependencies by running ./setup.sh, configure settings.toml
and .secrets.toml then run ./start_gps.py

A common evaluation usecase is:
Running "cgps" in the foreground to monitor GPS data, along with PointPerfect
GNSS corrections.

To do this, you would edit the credentials in the secret settings file as per the PointPerfect site,
set run_pygnssutils_in_foreground to false, and set the foreground process to "cgps".
To use cgps with the script, you also must enable the gpsd bridge. The default settings
will be OK in most instances.

Another usecase may be configuring and viusalizing the GPS data in u-center.
u-center is a Windows application, but it nevertheless can be both powerful in configuring 
and visualizing the GPS. To use u-center, you do NOT want to use our script, rather
just use a one line command to send all /dev/ttyACM0 data over TCP.

$ socat TCP-LISTEN:12345,reuseaddr,fork /dev/ttyACM0,raw,echo=0

TROUBLESHOOTING:
If you're getting 0,0,-17 as a coordinate, make sure that your antenna is connected well.
Ensure python is updated, the script used Python 3.10.12.

Now you're ready. Build great things.


