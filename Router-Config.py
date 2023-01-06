# Created by Nathan Cross 000809011.

import datetime
import ipaddress
import sys
import time
import urllib.parse
import urllib.request
import warnings

import pytz
import requests
import serial.tools.list_ports
from timezonefinder import TimezoneFinder
from tqdm import tqdm

if "bar" in (sys.argv[0]):
    progressBar = True
else:
    progressBar = False

print("Router Configuration")

# Tests connection to the internet
def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False


# Verifies if the IP passes is real
def verifyIP(prompt):
    IP = input(prompt)
    ipadd = False
    while ipadd == False:
        try:
            ipaddress.ip_address(IP)  # Checks if IP address is valid
            ipadd = True
        except ValueError:
            print(IP + " Is not a valid IP Address.")
            IP = input(prompt)
    return IP


# Checks and requests a 'yes' or 'no' answer
def yes_no(choice):
    yes = ['yes', 'ye', 'y']
    no = ['no', 'n']
    while True:
        choice = choice.lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("No a 'yes' or 'no'!\n")
            choice = input("Enter 'yes/no': ").lower()


# Creates a list of serial com ports
ports = serial.tools.list_ports.comports()
for port in ports:  # Searches through the list of ports to find the serial port.
    serialPort = port.name
    print("Serial Port Found: " + serialPort)
if len(ports) > 1:
    serialPort = input(str(len(ports)) + " Serial Ports found. Please Enter Specific Port Name: ")
if not ports:  # If no serial port is found then program will stop running
    print("No Serial Port Found! Attach Serial Port before Running!")
    time.sleep(4)
    exit()

print('Warning, Do not run while existing serial connection is open!')

itemModel = "ISR4321/K9"
print("Checking if Router is Model: " + itemModel)
ser = serial.Serial(str(serialPort))
if ser.is_open:
    ser.close()
ser.open()
time.sleep(1)

time.sleep(2)
ser.write(('      ' + '\r\nenable\r').encode("utf-8"))
time.sleep(1)
ser.write(('      ' + '\r\nenable\r').encode("utf-8"))


time.sleep(0.5)
ser.write(('  ' + "show inventory | include PID:").encode("utf-8"))  # Writes the line
ser.write((' \r').encode("utf-8"))  # Presses enter

time.sleep(1)
hardware = (ser.read(ser.inWaiting()).decode("utf-8"))  # Reads any responses that were not already read

if itemModel not in hardware:
    if not yes_no(input("Device is not an "+itemModel+"! Continue at your OWN RISK! y/n:")):
        exit("No chosen, exiting.")

    else:
        print("Continuing at your Own Choice!!")

else:
    print("Hardware " +itemModel+ " found!")

print("\n")
ser.close()  # Closes the serial connection



if connect():  # Uses the 'connect()' module to check for a internet connection
    while True:
        try:
            address = input("Enter Name of Location (Example: Hamilton, Ontario): ")  # Asks for location
            url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
            warnings.filterwarnings("ignore")  # Disables warning due to the SSL error of Waste Connections
            response = requests.get(url, verify=False).json()  # Requests information from website and stores it
            warnings.filterwarnings("default")  # Enables warnings again after getting page
            latitude = float(response[0]["lat"])  # Uses response to find latitude
            longitude = float(response[0]["lon"])  # Uses response to find longitude
            print("Location Found: " + response[0]["display_name"])  # Displays the found locations name

            obj = TimezoneFinder()
            timezoneLocation = obj.timezone_at(lng=longitude, lat=latitude)  # Finds timezone location from long and lat
            timeZoneOffsetSummer = str(pytz.timezone(timezoneLocation).localize(datetime.datetime(int(datetime.date.today().year), 6, 1)).strftime('%z').strip("0"))  # Finds the UTC offset in the summer
            timeZoneOffsetWinter = str(pytz.timezone(timezoneLocation).localize(datetime.datetime(int(datetime.date.today().year), 12, 1)).strftime('%z').strip("0"))  # Finds the UTC offset in the winter
            if timeZoneOffsetSummer != timeZoneOffsetWinter:  # Checks for a difference in UTC offset from summer to winter
                print("Day Lights Saving time Detected")
                isDST = True
            else:
                isDST = False

            print(timezoneLocation + " UTC: " + timeZoneOffsetWinter)  # Prints timezone location and the UTC offset
            timeZoneOffset = timeZoneOffsetWinter
            break
        except:
            print("Enter a Real location!")
else:
    print("Network Connection Not Found! Manual Timezone Selection Required.")  # Only displays if no internet connection
    while True:
        try:
            timeZoneOffset = int(input("Enter NON-DST Timezone Offset from UTC (Example: -5): "))  # Asks for manual UTC offset
            if 12 >= timeZoneOffset >= -11:  # Checks if input is within possible timezone range
                break
            else:
                print("Timezone is outside possible range!")
        except:
            print("Not a number!")
    if yes_no(input("Is there daylights savings time at this location? Enter 'Yes/No': ")):
        isDST = True
        print("Yes Selected")
    else:
        isDST = False
        print("No Selected")

if isDST:
    DSTOption = 'clock summer-time DST recurring'  # If timezone is detected then adds line to code
else:
    DSTOption = '!'  # If timezone is not detected then blank line is added instead

while True:
    hostName = input("Enter Device Hostname: ")  # Asks for hostname of Router
    if len(hostName) < 2:  # Produces error if hostname is not entered
        print("Enter a Hostname!")
    else:
        break

while True:
    enableSecret = input("Enter Device Enable Password: ")  # Asks for Password for Router
    if len(enableSecret) < 2:  # Produces error if Password is not entered
        print("Enter a Password!")
    else:
        break

while True:
    rootSecret = input("Enter Root Password: ")  # Asks for Password for Router
    if len(rootSecret) < 2:  # Produces error if Password is not entered
        print("Enter a Password!")
    else:
        break

while True:
    ipXVariable = input("Enter Device Specific IP Variable (x): ")  # Asks for device specific IP variable
    if (not ipXVariable.isdigit()) or int(ipXVariable) > 255:  # Checks if ip is just number
        print("Enter just the IP number!")
    else:
        break

if yes_no(input("Is WAN connection DHCP? Enter 'yes/no': ")):  # Asks if device uses DHCP for WAN
    wanItems = "dhcp"  # Adds lines to cisco code
    wanDefGate = "dhcp"
    print("DHCP Accepted")
else:
    print("Static Chosen")  # If DHCP is not chosen, static IP is requested
    wanIP = verifyIP("Enter WAN IP: ")  # Requests WAN IP address and verifies it
    wanSub = verifyIP("Enter WAN Subnet MASK (Example: 255.255.255.0): ")  # Requests Subnet Mask Address
    wanItems = wanIP + " " + wanSub
    wanDefGate = verifyIP("Enter WAN Default Gateway IP to Static Route (Example: 50.244.106.206): ")  # Requests Default Gateway


DHCPInput = ""  # Creates blank variable
excludedAddresses = ""
if yes_no(input("Are there any extra DHCP addresses to exclude? Yes/No: ")):  # Asks if extra DHCP addresses to exclude
    while True:
        DHCPInput = input("\nIf there are any DHCP excluded addresses enter them below, else leave blank:\nip dhcp excluded-address ")
        if DHCPInput == "":
            break
        else:
            while True:
                try:
                    for i in DHCPInput.split(" "):  # Allows the checking of multiple IP addresses
                        ipaddress.ip_address(i)
                    break
                except ValueError:  # If IP not valid, produces errors and asks for new address
                    print(DHCPInput + " Is not a valid IP Address(es).")
                    DHCPInput = input("\nIf there are any DHCP excluded addresses enter them below, else leave blank:\nip dhcp excluded-address ")
            excludedAddresses = excludedAddresses + "ip dhcp excluded-address " + DHCPInput + "\n"  # Adds excluded address to the list

# Config for the router with variables
config = '''Config t
!
hostname ''' + hostName + '''
!
no ip domain-lookup
!
clock timezone UTC ''' + str(timeZoneOffset) + '''	
''' + DSTOption + '''
ntp server 129.6.15.28
service timestamps log datetime localtime show-timezone
!
enable secret ''' + enableSecret + '''
!
''' + excludedAddresses + '''
!
ip dhcp pool LAN
 network 10.100.''' + ipXVariable + '''.0 255.255.255.0
 dns-server 9.9.9.9 1.1.1.1
 domain-name example.com
 default-router 10.100.''' + ipXVariable + '''.1
 lease 0 12 
!         
ip dhcp pool Guest
 network 192.168.1.0 255.255.255.0
 default-router 192.168.1.1
 dns-server 9.9.9.9 1.1.1.1
!
ip domain name example.com
!
no service config
!
username root privilege 15 secret ''' + rootSecret + '''
!
crypto key generate rsa modulus 1024
ip ssh time-out 60
ip ssh authentication-retries 2
ip ssh version 2
!
End

Config t
!
interface GigabitEthernet0/0/0
 description WAN-CONNECTION
 ip address ''' + wanItems + '''
 ip nat outside
no shut
!
!
end

Config t
!
router eigrp 10
 network 10.2.252.''' + ipXVariable + ''' 0.0.0.0
 redistribute connected route-map EIGRP-TAG
 eigrp router-id 10.2.252.''' + ipXVariable + '''
!
router eigrp 15
 network 10.2.236.''' + ipXVariable + ''' 0.0.0.0
 redistribute connected route-map EIGRP-TAG
 eigrp router-id 10.2.236.''' + ipXVariable + '''
!
!
ip forward-protocol nd
no ip http server
no ip http secure-server
!
!
ip nat inside source list PAT interface GigabitEthernet0/0/0 overload
ip route 0.0.0.0 0.0.0.0 GigabitEthernet0/0/0 ''' + wanDefGate + '''
!
ip ssh time-out 60
ip ssh authentication-retries 2
ip ssh version 2
!
!
!
ip access-list standard ssh
permit 10.0.0.0 0.255.255.255
!
ip access-list extended Guest
 deny   ip any 10.0.0.0 0.255.255.255
 permit ip any any
ip access-list extended PAT
 permit ip 10.100.''' + ipXVariable + '''.0 0.0.0.255 any
 permit ip 172.16.1.0 0.0.0.255 any
!
end

Config t
!
banner login ~
**************************************************************************
**************************************************************************
WARNING! Access to this device is restricted to those individuals with 
specific permissions. If you are not an authorized user, disconnect now.
Any attempts to gain unauthorized access will be prosecuted to the fullest
extent of the law By using this system, the user consents to such
interception, monitoring, recording, copying, auditing, inspection, and
disclosure at the discretion of authorized site personnel. Unauthorized or
improper use of this system may result in administrative disciplinary action
and civil and criminal liability. By continuing to use this system you 
indicate your awareness of and consent to these terms and conditions of use.
LOG OFF IMMEDIATELY if you do not agree 
to the conditions stated in this warning.
**************************************************************************
~
!
End

Config t
no ip nat service sip udp port 5060
no ip nat service sip tcp port 5060
end

Config t
!
line con 0
 login local
 stopbits 1
line 1
 modem InOut
 flowcontrol hardware
line aux 0
!
!
!
!
End

Config t
!
interface GigabitEthernet0
 no ip address
 shutdown
 description LAN-Switch1
!
interface GigabitEthernet0/0/1
 no ip address
 shutdown
 description LAN-Switch2
!
interface Serial0/1/0
 no ip address
 shutdown 
!
interface Serial0/1/1
 no ip address
 shutdown
!
End

Config t
!
Config-register 0x2102
!
end
!
'''

# Checks if the serial port is open, if it is, then it closes and then opens a new session
ser = serial.Serial(str(serialPort))
if ser.is_open:
    ser.close()
ser.open()
time.sleep(1)

# Clears the previous inputs
ser.flushInput()
ser.flush()

# Switches device into enable mode
time.sleep(2)
ser.write(('      ' + '\r\nenable\r').encode("utf-8"))
time.sleep(1)
ser.write(('      ' + '\r\nenable\r').encode("utf-8"))

# Takes the config and splits it into lines that will be used
splitConfig = config.split("\n")

if progressBar:
    for i in tqdm(splitConfig):  # Goes through each line of the config
        time.sleep(0.2)
        ser.write(('  ' + i).encode("utf-8"))  # Writes the line
        ser.write((' \r').encode("utf-8"))  # Presses enter
        pass
else:
    for i in splitConfig:  # Goes through each line of the config
        time.sleep(0.2)
        ser.write(('  ' + i).encode("utf-8"))  # Writes the line
        ser.write((' \r').encode("utf-8"))  # Presses enter
        print(ser.read(ser.inWaiting()).decode("utf-8"), end="")  # Reads the response

writeRequest = yes_no(input("\nWould you like to Write to Memory?: "))
if writeRequest:
    time.sleep(1)
    ser.write(('      ' + '\r\nwr\r').encode("utf-8"))

else:
    print("Not Written To Memory!")

time.sleep(1)
print(ser.read(ser.inWaiting()).decode("utf-8"), end="")  # Reads any responses that were not already read
print("\n")
ser.close()  # Closes the serial connection

print("\n\n\nRouter Configuration Completed!")
input(":Press ENTER to close:")
