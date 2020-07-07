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
import getpass
from OSC import OSCClient, OSCMessage, OSCServer
from shutil import copyfile


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
# /interrupteur/... are interrupteur messages (from/to)
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
# interrupteur = ????:??
################################################


RADIOLOGIC_PATH = "/home/pi/Documents/radiologic2"
UNIVERSALMEDIAPLAYER_PATH = "/home/pi/Documents/openFrameworks/apps/universalMediaPlayer"
VERMUTH_PATH = "/home/pi/Documents/vermuth"
isPi = True
if (platform.machine().startswith("x86")):
    isPi = False
    if(platform.system() == "Darwin" and getpass.getuser()=='adminmac'):
        #mac os et Aurelien Conil
        RADIOLOGIC_PATH = "/Users/adminmac/Boulot/Radiologic/GIT/radiologic2"
        UNIVERSALMEDIAPLAYER_PATH = "/Users/adminmac/Boulot/Universal-Media-Player/GIT/universalMediaPlayer"
        VERMUTH_PATH = "/Users/adminmac/Boulot/vermuth"
    elif(platform.system() == "Darwin" and getpass.getuser()!='collor_nor'):
        #print("Martin Rossi, tu dois mettre les chemin a l'interrieur du programme python")
        #mac os et Martin Rossi (COLL OR_NOR)
        RADIOLOGIC_PATH = "/Users/collor_nor/Documents/DEV/repos/Radiologic\ Project/radiologic2"
        UNIVERSALMEDIAPLAYER_PATH = "/Users/collor_nor/Documents/DEV/repos/Radiologic\ Project/universalMediaPlayer"
        VERMUTH_PATH = "/Users/collor_nor/Documents/DEV/repos/Radiologic\ Project/vermuth"
    else :
        # ORDINATEUR DE MARTIN
        RADIOLOGIC_PATH = "/home/tinmar/Dev/ornormes/radiologic2"
        UNIVERSALMEDIAPLAYER_PATH = "/home/tinmar/Dev/ornormes/universalMediaPlayer"
        VERMUTH_PATH = "/home/tinmar/Dev/vermuth"

USER_SETTINGS_PATH = RADIOLOGIC_PATH+"/UserSettings.json"
GLOBAL_SETTINGS_PATH = RADIOLOGIC_PATH+"/datajson.json"
DEFAULT_GLOBAL_SETTINGS_PATH = RADIOLOGIC_PATH+"/datajson.default.json"


class SimpleServer(OSCServer):
    def __init__(self, t):
        OSCServer.__init__(self, t)
        self.selfInfos = t
        self.addMsgHandler('default', self.handleMsg)

    def handleMsg(self, oscAddress, tags, data, client_address):
        global machine
        global client
        global isPlayingMovie
        print("OSC message received on : "+oscAddress)
        print(data)

        splitAddress = oscAddress.split("/")
        print(splitAddress)

        ##### from ofUniversalMediaPlayer ####
        if(splitAddress[1] == "videoPlayingState"):
            isPlayingMovie = data[0]>0
            forwardMsgToOf(buildSimpleMessage("/averageColor/activate",1 if isPlayingMovie else 0,"i"))
            if(not isPlayingMovie):
                presetToRecall = lastVermuthPreset or confSettings["light"]["defaultStateName"]
                setVermuthState(presetToRecall)
            
            
        ############## APP itself #############
        elif(splitAddress[1] == "app"):
            if(splitAddress[2] == "veille"):
                v = len(data) == 0 or data[0] == 1
                setVeille(v)

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
            if(splitAddress[2] == "update_vermuth"):
                print("update Universal Media Player")
                quit_app()
                time.sleep(2)
                update_vermuth()
                start_app()

            if(splitAddress[2] == "update"):
                print("update Radiologic2")
                quit_app()
                update()
                reboot()
            if(splitAddress[2] == "update_all"):
                update_all()

        ############## RPI itself #############
        elif(splitAddress[1] == "rpi"):
            if(splitAddress[2] == "shutdown"):
                print("Turning off the rpi")
                setVeille(True)
                powerOff()
            if(splitAddress[2] == "reboot"):
                print("Reboot the machine")
                setVeille(True)
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
                # out from services mode if any light state are called
                setServices(False,False)
                setVermuthState(data)
            else:
                print("Forwarding not supported for light/", splitAddress[2])
        ########### HANDLE "SERVICE" MODE #########
        elif((splitAddress[1] == "interrupteur" and splitAddress[2] == "services") or splitAddress[1] == "services"):
            v = len(data) == 0 or data[0] == 1
            setServices(v,True)

        elif splitAddress[1] == "settings":
            if(splitAddress[2] == "masterLight"):
                sendMasterLight(getFloat(data[0]))
            elif(splitAddress[2] == "volume"):
                sendVolume(getFloat(data[0]))
            elif(splitAddress[2] == "save"):
                saveSettings()

        elif( splitAddress[1] == "averageColor"):
            if(isPlayingMovie and splitAddress[2]=="color"):
                setVermuthColor(data[0]/255.0,data[1]/255.0,data[2]/255.0)
        elif(splitAddress[1] == "echo"):
            oscmsg = OSCMessage()
            oscmsg.setAddress(oscAddress)
            oscmsg.setAddress("/pong")
            forwardMsgToWebApp(oscmsg)

        ############ FORWARD TO WEBAPP #######
        elif(False):
            oscmsg = OSCMessage()
            oscmsg.setAddress(oscAddress)
            oscmsg.append(data)
            forwardMsgToWebApp(oscmsg)


veille = False
isPlayingMovie = False
lastVermuthPreset = ""

def getFloat(strOrFloat):
    return float(strOrFloat)

def setVermuthState(name, time=-1):
    global lastVermuthPreset
    print('setting state %s'%name)
    if (name!= confSettings["light"]["servicesStateName"]) and( name != confSettings["light"]["veilleStateName"]):
        lastVermuthPreset = name
    if(time == -1):
        time = getFloat(confSettings["light"]["fadeTime"])
    oscmsg = OSCMessage()
    oscmsg.setAddress("/sequencePlayer/goToStateNamed")
    oscmsg.append(name)
    oscmsg.append(time)
    forwardMsgToVermuth(oscmsg)

def setVermuthColor(r,g,b):
    oscmsg = OSCMessage()
    oscmsg.setAddress("/allColors")
    w = confSettings["video"]["videoColorWeights"]
    oscmsg.append(r*w[0],"f")
    oscmsg.append(g*w[1],"f")
    oscmsg.append(b*w[2],"f")
    forwardMsgToVermuth(oscmsg)

services = False
def setServices(v,notifyVermuth):
    global services
    services = v
    if(notifyVermuth):
        setVermuthState(confSettings["light"]["servicesStateName" if services else "veilleStateName"],0)
    else:
        forwardMsgTointerrupteur(buildSimpleMessage("/interrupteur/services",0 if services else 1))




def setVeille(v):
    global veille
    print("going to sleep mode : ", v)
    setServices(False,False)
    print("notifying veille")
    veille = v
    forwardMsgToWebApp(buildSimpleMessage("/app/veille",1 if v else 0))
    forwardMsgToOf(buildSimpleMessage("/messages/message",""))
    
    if v:
        setVermuthState(confSettings["light"]["servicesStateName"])
        oscmsg = OSCMessage()
        oscmsg.setAddress("/player/stop")
        forwardMsgToOf(oscmsg)
    else:
        setVermuthState(confSettings["light"]["defaultStateName"])
    cmd = ["vcgencmd","display_power","0" if v else "1"]    
    print(cmd)
    if isPi:
        subprocess.Popen(cmd)
    


def forwardMessage(client, msg):
    try:
        client.send(msg)
        # msg.clearData()
    except Exception, e:
        print(" error on sending to client ")
        print(e)


def forwardMsgToOf(msg):
    forwardMessage(client_of, msg)


def forwardMsgTointerrupteur(msg):
    client_interrupteur.safeSend(msg)


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

def buildSimpleMessage(addr,arg = None,_type=None):
    oscmsg = OSCMessage()
    oscmsg.setAddress(addr)
    if(arg !=None):
        oscmsg.append(arg,_type)
    return oscmsg

def sendInitConfigToApps():
    # this function sends config from datajson/metadata to launched apps
    forwardMsgToOf(buildSimpleMessage("/player/vflip",1 if confSettings["video"]["vFlip"] else 0,"f"))
    forwardMsgToOf(buildSimpleMessage("/player/hflip",1 if confSettings["video"]["hFlip"] else 0,"f"))
    forwardMsgToOf(buildSimpleMessage("/averageColor/smooth",getFloat(confSettings["video"]["averageColorSmooth"])))
    sendVolume(getFloat(userSettingsData['volume']))
    sendMasterLight(getFloat(userSettingsData["masterLight"]))
    setVeille(False)

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

def send_busy(v):    
    oscmsg = OSCMessage()
    oscmsg.setAddress("/app/busy")
    oscmsg.append(v)
    forwardMsgToWebApp(oscmsg)
    

def closing_app():
    global runningApp
    runningApp = False
    print("Closing App")


def quit_app():
    print("========= QUIT ALL APP ======")
    send_busy(1)
    os.chdir(RADIOLOGIC_PATH+"/script")
    subprocess.call(["./quit.sh"])
    send_busy(0)
    print("======== ALL APP QUITTED ====")


def update_of():
    print("========= UPDATE OF APP ======")
    send_busy(1)
    os.chdir(UNIVERSALMEDIAPLAYER_PATH+"/script")
    subprocess.call(["./update.sh"])
    send_busy(0)
    print("========= OF APP UPDATED ======")


def update_vermuth():
    print("========= UPDATE VERMUTH APP ======")
    send_busy(1)
    os.chdir(VERMUTH_PATH)
    subprocess.call(["./update.sh"])
    send_busy(0)
    print("========= OF APP UPDATED ======")


def update():
    print("========= UPDATE RADIOLOGIC2 ======")
    send_busy(1)
    os.chdir(RADIOLOGIC_PATH+"/script")
    subprocess.call(["./update.sh"])
    send_busy(0)
    print("========= RADIOLOGIC2 then reboot ======")


def update_all():
    print("update all")
    quit_app()
    update_of()
    update()
    update_vermuth()
    reboot()


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
    print('setting volume',v)
    v = getFloat(v)
    global userSettingsData
    userSettingsData["volume"] = v
    oscmsg = OSCMessage()
    oscmsg.setAddress("/player/volume")
    volMultiplier = 0.5
    oscmsg.append(v*volMultiplier,"f")
    forwardMsgToOf(oscmsg)


def sendMasterLight(v):
    global userSettingsData
    v = getFloat(v)
    userSettingsData["masterLight"] = v
    oscmsg = OSCMessage()
    oscmsg.setAddress("/universe/setGrandMaster")
    oscmsg.append(v)
    forwardMsgToVermuth(oscmsg)


class SafeOSCClient(OSCClient):
    def __init__(self, ipPortTuple):
        OSCClient.__init__(self)
        self.ipPortTuple = ipPortTuple
        self.isConnected = False
        self.tryConnect()

    def tryConnect(self):
        try:
            print("trying to connect to ",self.ipPortTuple[0], self.ipPortTuple[1])
            self.connect((self.ipPortTuple[0], self.ipPortTuple[1]))
            self.isConnected = True
        except Exception, e:
            print("can't connect",e)
            self.isConnected = False

    def safeSend(self, msg):
        if(self.isConnected):
            try:
                self.send(msg)
            except Exception, e:
                self.tryConnect()
        else:
            self.tryConnect()

userSettingsData = {
    "volume": 0.5,
    "masterLight": 1,
}

confSettings = {
    '''
    !!! do not modify this , cf README change metadata in  datajson.json!!!
    "light": {
        "fadeTime": 3,
        "veilleStateName": "__black",
        "defaultStateName": "__full"
    },
    "video": {
        "vFlip": 1  
    },
    "interrupteur": {
        "ip": "192.168.0.102",
        "port": 12347
    }'''
}



def saveSettings():
    global userSettingsData
    if(not ("volume" in userSettingsData) or not ("masterLight" in userSettingsData)):
        print("invalid settings ", userSettingsData)
        return

    with open(USER_SETTINGS_PATH, 'w') as fp:
        try:
            json.dump(userSettingsData, fp)
        except Exception, e:
            print("error saving settings", e, userSettingsData)
        print("settings", userSettingsData)


def initSettings():
    global userSettingsData
    global confSettings
    # save default user settings if non existent
    if(not os.path.exists(USER_SETTINGS_PATH)):
        print("creating default user settings", userSettingsData)
        saveSettings()
    # load existing user settings
    with open(USER_SETTINGS_PATH, 'r') as userFp:
        userSettingsData = json.load(userFp)


    # checking if new option have been added in  default datajson.default/metadata and merge them in datajson/metadata if needed
    if(not os.path.exists(GLOBAL_SETTINGS_PATH)):
        copyfile(DEFAULT_GLOBAL_SETTINGS_PATH, GLOBAL_SETTINGS_PATH)
    with open(DEFAULT_GLOBAL_SETTINGS_PATH, 'r') as defFp:
        defCfgFile = json.load(defFp)
    with open(GLOBAL_SETTINGS_PATH, 'r') as curFp:
        curCfgFile = json.load(curFp)
    
    if(not "metadata" in curCfgFile):
        curCfgFile["metadata"] = {}
    confSettings = curCfgFile["metadata"]
    defCfg = defCfgFile["metadata"]
    hasMerge = False
    for (k, v) in defCfg.items():
        for (kk, vv) in v.items():
            if (not k in confSettings):
                confSettings[k] = {}
                hasMerge = True
            if (not kk in confSettings[k]):
                confSettings[k][kk] = vv
                hasMerge = True

    if hasMerge:
        print ("merged some")
        with open(GLOBAL_SETTINGS_PATH, 'w') as fp:
            json.dump(confSettings, fp, indent=2)
    print("settings are : ")
    print(json.dumps(confSettings,indent=2))



def main():

    print(" ===== init settings ====")
    # will ensure any default settings are present in datajson/metadata
    initSettings()


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

    global client_interrupteur
    client_interrupteur = SafeOSCClient(
        (confSettings["interrupteur"]["ip"], confSettings["interrupteur"]["port"]))

    # START ON BOOT
    start_app()
    time.sleep(5)
    print(" ===== sending config to apps ====")
    sendInitConfigToApps()

    # MAIN LOOP
    global runningApp
    runningApp = True

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
