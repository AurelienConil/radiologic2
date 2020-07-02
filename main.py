import os
import sys
import glob
import time
import threading
import struct
import socket
import subprocess
import platform
import json
from OSC import OSCClient, OSCMessage, OSCServer

#################################################
# This is Radiologic Deamon
# Always running
# start & stop all programs needed for Radiologic
# turn off rpi, manage update,
# dispi osc message
#################################################

################################################
# /player/...  are messages for OF app
# /messages/... are messages for OF app
# /rpi/... are system messages
# /interupteur/... are interupteur messages (from/to)
################################################

################################################
# Script and app are launched through subprocess module
# subprocess.Popen is nonblocking
# subprocess.call are blocking
################################################


################################################
#           PORTS
# OF_APP in = 12343
# OF_web in =  12342
# Python in = 12344
# webapp in = 12345
# vermuth in = 3000
# interupteur = ????:??
################################################


RADIOLOGIC_PATH = "/home/pi/Documents/radiologic2"
UNIVERSALMEDIAPLAYER_PATH = "/home/pi/Documents/openFrameworks/apps/universalMediaPlayer"
VERMUTH_PATH = "/home/pi/Documents/vermuth"

if (platform.machine().startswith("x86")):
    RADIOLOGIC_PATH = "/home/tinmar/Dev/ornormes/radiologic2"
    UNIVERSALMEDIAPLAYER_PATH = "/home/tinmar/Dev/ornormes/universalMediaPlayer"
    VERMUTH_PATH = "/home/tinmar/Dev/vermuth"

SETTINGS_PATH = RADIOLOGIC_PATH+"/settings.json"


class SimpleServer(OSCServer):
    def __init__(self, t):
        OSCServer.__init__(self, t)
        self.selfInfos = t
        self.addMsgHandler('default', self.handleMsg)

    def handleMsg(self, oscAddress, tags, data, client_address):
        global machine
        global client
        print("OSC message received on : "+oscAddress)

        splitAddress = oscAddress.split("/")
        print(splitAddress)

        ############## APP itself #############
        if(splitAddress[1] == "app"):
            if(splitAddress[2] == "saveSettings"):
                saveSettings()
            if(splitAddress[2] == "close"):
                print("closing the app")
                quit_app()
            if(splitAddress[2] == "start"):
                print("starting the app")
                start_app()
            if(splitAddress[2] == "restart"):
                print("restart the app")
                quit_app()
                time.sleep(2)
                start_app()
            if(splitAddress[2] == "update_of"):
                print("update Universal Media Player")
                quit_app()
                time.sleep(2)
                update_of()
                start_app()
            if(splitAddress[2] == "update"):
                print("update Radiologic2")
                quit_app()
                update()
                reboot()
            if(splitAddress[2] == "update_all"):
                print("update all")
                quit_app()
                update_of()
                update()
                reboot()

        ############## RPI itself #############
        elif(splitAddress[1] == "rpi"):
            if(splitAddress[2] == "shutdown"):
                print("Turning off the rpi")
                powerOff()
            if(splitAddress[2] == "reboot"):
                print("Reboot the machine")
                reboot()
        ############ FORWARD TO OPENSTAGECONTROL ###
        elif(splitAddress[1] == "player" or splitAddress[1] == "message"):
                oscmsg = OSCMessage()
                oscmsg.setAddress(oscAddress)
                oscmsg.append(data)
                forwardMsgToOf(oscmsg)
        ############ FORWARD TO OF_WEB ######
        elif(splitAddress[1] == "addMovie" or splitAddress[1] == "playPercentage" or splitAddress[1] == "playIndex"):
            oscmsg = OSCMessage()
            oscmsg.setAddress(oscAddress)
            oscmsg.append(data)
            forwardMsgToOfWeb(oscmsg)

        ########### FORWARD TO VERMUTH #######
        elif(splitAddress[1] == "light"):
            if(splitAddress[2] == "preset"):
                setVeille(data=="veille") # out from veille mode if other lilght state are called
                oscmsg = OSCMessage()
                oscmsg.setAddress("/stateList/recallStateNamed")
                oscmsg.append(data)
                forwardMsgToVermuth(oscmsg)
            else:
                print("Forwarding not supported for light/", splitAddress[2])
        ########### HANDLE "VEILLE" MODE #########
        elif((splitAddress[1] == "interupteur" and splitAddress[2] == "veille") or splitAddress[1] == "veille"):
            v = len(data) == 0 or data[0] == 1
            setVeille(v)
            oscmsg = OSCMessage()
            oscmsg.setAddress(oscAddress)
            oscmsg.append(data)
            forwardMsgToVermuth(oscmsg)
        elif splitAddress[1] == "settings" :
            if(splitAddress[2]== "masterLight"):
                sendMasterLight(data[0])
            elif(splitAddress[2]== "volume"):
                sendVolume(data[0])
            elif(splitAddress[2]=="save"):
                saveSettings()

        ############ FORWARD TO WEBAPP #######
        elif(False):
            oscmsg = OSCMessage()
            oscmsg.setAddress(oscAddress)
            oscmsg.append(data)
            forwardMsgToWebApp(oscmsg)


veille = False



def setVeille(v):
    print("going to sleep mode : ", v)
    global veille
    veille = (1 if v == 1 else 0)
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscAddress)
    oscmsg.append(v)
    forwardMsgToInterupteur(oscmsg)


def forwardMessage(client, msg):
    try:
        client.send(msg)
        # msg.clearData()
    except Exception, e:
        print(" error on sending to client ")
        print(e)


def forwardMsgToOf(msg):
    forwardMessage(client_of, msg)


def forwardMsgToInterupteur(msg):
    client_interupteur.safeSend(msg)


def forwardMsgToOfWeb(msg):
    forwardMessage(client_ofWeb, msg)


def forwardMsgToWebApp(msg):
    forwardMessage(client_webapp, msg)


def forwardMsgToVermuth(msg):
    forwardMessage(client_vermuth, msg)

    # EXEMPLE HOW TO SEND AN OSC MESSAGE
    # oscmsg = OSC.OSCMessage()
    # oscmsg.setAddress("/startup")
    # oscmsg.append('HELLO')
    # c.send(oscmsg)


def powerOff():

    time.sleep(5)
    print("========= POWER OFF ======")
    os.chdir(RADIOLOGIC_PATH+"/script")
    subprocess.call(['./shutdown.sh'])


def reboot():

    time.sleep(5)
    print("========= POWER OFF ======")
    os.chdir(RADIOLOGIC_PATH+"/script")
    subprocess.call(['./reboot.sh'])


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def closing_app():
    global runningApp
    runningApp = False
    print("Closing App")


def quit_app():
    print("========= QUIT ALL APP ======")
    os.chdir(RADIOLOGIC_PATH+"/script")
    subprocess.call(["./quit.sh"])
    print("======== ALL APP QUITTED ====")


def update_of():
    print("========= UPDATE OF APP ======")
    os.chdir(UNIVERSALMEDIAPLAYER_PATH+"/script")
    subprocess.call(["./update.sh"])
    print("========= OF APP UPDATED ======")


def update():
    print("========= UPDATE RADIOLOGIC2 ======")
    os.chdir(RADIOLOGIC_PATH+"/script")
    subprocess.call(["./update.sh"])
    print("========= RADIOLOGIC2 then reboot ======")


def launchCmd(dir, cmd):
    try:
        os.chdir(dir)
        subprocess.Popen(cmd)
    except Exception, e:
        print(" error on running cmd " + str(cmd))
        print(e)


def start_app():

    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        print("========= START OF_APP ======")
        launchCmd(UNIVERSALMEDIAPLAYER_PATH +
                  "/of_universalMediaPlayer/bin", ["./of_universalMediaPlayer"])
        print("========= START OF_webapp =======")
        launchCmd(UNIVERSALMEDIAPLAYER_PATH+"/node", ["node", "."])
        print("========= START RADIOLOGIC2 webapp =======")
        launchCmd(RADIOLOGIC_PATH+"/webapp", ["node", "."])
        print("========= START VERMUTH ======")
        launchCmd(VERMUTH_PATH, ["./run.sh"])  # TODO start node instead

        ########################
        # exemple using POPEN : which is a non blocking process
        # cmd = ["pd",  "-nogui",  "-jack",  "/home/pi/lucibox/machines/"+str(machine)+"/nogui.pd"]
        # subprocess.Popen(cmd)
        # print("======== PUREDATA STARTED ====")
        # print("========= START OPEN STAGE CONTROL ======")
        # cmd = ["node",  "/home/pi/open-stage-control/app",  "-l",  "/home/pi/lucibox/machines/"+str(machine)+"/osc.json", "-s", "127.0.0.1:9999", "-o", "9998"]
        # subprocess.Popen(cmd)
        # print("========= OPEN STAGE CONTROL STARTED ======")


def sendVolume(v):
    settingsData["volume"] = v
    oscmsg = OSCMessage()
    oscmsg.setAddress("/player/volume")
    oscmsg.append(v)
    forwardMsgToOf(oscmsg)

def sendMasterLight(v):
    settingsData["masterLight"] = v
    oscmsg = OSCMessage()
    oscmsg.setAddress("/universe/setGrandMaster")
    oscmsg.append(v)
    forwardMsgToVermuth(oscmsg)


class SafeOSCClient(OSCClient):
    def __init__(self, ipPortTuple):
        self.ipPortTuple = ipPortTuple
        self.tryConnect()

    def tryConnect(self):
        try:
            self.connect((self.ipPortTuple[0], self.ipPortTuple[1]))
            self.isConnected = True
        except Exception, e:
            self.isConnected = False

    def safeSend(msg):
        if(isConnected):
            try:
                self.send(msg)
            except Exception, e:
                self.tryConnect()

settingsData = {
    "volume":1,
    "masterLight":1

}
def loadSettings():
    with  open(SETTINGS_PATH,'r') as fp:
        try:
            loodedSettings = json.load(fp)
        except Exception, e:
            print("error loading settings",e)
        print("settings",loodedSettings)
        if loodedSettings:
            if( "volume" in loodedSettings):
                sendVolume(loodedSettings["volume"])
            if( "masterLight" in loodedSettings):
                sendMasterLight(loodedSettings["masterLight"])

def saveSettings():
    global settingsData
    if( not ("volume" in settingsData )or not ("masterLight" in settingsData) ):
        print("invalid settings ",settingsData)
        return 

    with  open(SETTINGS_PATH,'w') as fp:
        try:
                json.dump(settingsData,fp)
        except Exception, e:
            print("error saving settings",e,settingsData)
        print("settings",settingsData)
    

def main():

    # OSC SERVER
    # myip = get_ip()
    myip = "0.0.0.0"
    print("IP adress is : "+myip)
    try:
        server = SimpleServer((myip, 12344))
    except:
        print(" ERROR : creating server")
    print("server created")
    try:
        st = threading.Thread(target=server.serve_forever)
    except:
        print(" ERROR : creating thread")
    try:
        st.start()
    except:
        print(" ERROR : starting thread")

    print(" OSC server is running")

    # OSC CLIENT : OPENFRAMEWORKS APP
    global client_of
    client_of = OSCClient()
    client_of.connect(('127.0.0.1', 12343))

    # OSC CLIENT : OPENFRAMEWORKS WEB APP
    global client_ofWeb
    client_ofWeb = OSCClient()
    client_ofWeb.connect(('127.0.0.1', 12342))

    # OSC CLIENT : WEBAPP APP ( the one on this repo)
    global client_webapp
    client_webapp = OSCClient()
    client_webapp.connect(('127.0.0.1', 12345))

    # OSC CLIENT : VERMUTH APP
    global client_vermuth
    client_vermuth = OSCClient()
    client_vermuth.connect(('127.0.0.1', 11000))

    global client_interupteur
    client_interupteur = SafeOSCClient(('192.168.50.50', 3005))

    if(not os.path.exists(SETTINGS_PATH)):
        print("creating default settings",settingsData)
        saveSettings()
    # START ON BOOT
    start_app()

    # MAIN LOOP
    global runningApp
    runningApp = True
    print(" ===== Load settings ====")

    time.sleep(3)
    loadSettings()
    print(" ===== STARTING MAIN LOOP ====")
    while runningApp:
        # This is the main loop
        # Do something here
        try:
            time.sleep(1)
        except:
            print("User attempt to close programm")
            runningApp = False

    # CLOSING THREAD AND SERVER
    print(" Ending programme")
    server.running = False
    print(" Join thread")
    st.join()
    server.close()
    print(" This is probably the end")


if __name__ == "__main__":
    main()
