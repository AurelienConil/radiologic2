import os
import sys
import glob
import time
import threading
import struct
import socket
import subprocess 
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
# vermouth in = ??
################################################


class SimpleServer(OSCServer):
    def __init__(self,t):
        OSCServer.__init__(self,t)
        self.selfInfos = t
        self.addMsgHandler('default', self.handleMsg)

    
    def handleMsg(self,oscAddress, tags, data, client_address):
        global machine
        global client
        print("OSC message received on : "+oscAddress)

        splitAddress = oscAddress.split("/")
        print(splitAddress)
        
        ############## APP itself #############
        if(splitAddress[1]=="app"):
            if(splitAddress[2]=="close"):
                print("closing the app")
                quit_app()
            if(splitAddress[2]=="start"):
                print("starting the app")
                start_app()
            if(splitAddress[2]=="restart"):
                print("restart the app")
                quit_app()
                time.sleep(2)
                start_app()
            if(splitAddress[2]=="update_of"):
                quit_app()
                time.sleep(2)
                update_of()
                start_app()
            if(splitAddress[2]=="update"):
                quit_app()
                update()
                reboot()
            if(splitAddress[2]=="update_all"):
                quit_app()
                update_of()
                update()
                reboot()
                

        ############## RPI itself #############
        elif(splitAddress[1]=="rpi"):
            if(splitAddress[2]=="shutdown"):
                print("Turning off the rpi")
                powerOff();
            if(splitAddress[2]=="reboot"):
                print("Reboot the machine")
                reboot();
        ############ FORWARD TO OPENSTAGECONTROL ###
        elif(splitAddress[1]=="player" || splitAddress[1]=="message" ):
            oscmsg = OSC.OSCMessage()
            oscmsg.setAddress(oscAddress)
            oscmsg.append(data)
            forwardMsgToOf(oscmsg)
        ############ FORWARD TO OF_WEB ######
        elif(splitAddress[1]=="addMovie" || splitAddress[1]=="playPercentage" || splitAddress[1]=="playIndex" ):
            oscmsg = OSC.OSCMessage()
            oscmsg.setAddress(oscAddress)
            oscmsg.append(data)
            forwardMsgToOfWeb(oscmsg)
        ############ FORWARD TO WEBAPP #######
        elif( False ):
            oscmsg = OSC.OSCMessage()
            oscmsg.setAddress(oscAddress)
            oscmsg.append(data)
            forwardMsgToWebApp (oscmsg)
        ########### FORWARD TO VERMUTH #######
        elif( splitAddress[1]=="averageColor"):
            print("Forwarding to vermouth no implemeted yet")



def forwardMsgToOf(msg):
    try:
        client_of.sendto(msg)
        msg.clearData()
     except:
        print(" error on sending")

def forwardMsgToOfWeb(msg):
    try:
        client_ofWeb.sendto(msg)
        msg.clearData()
     except:
        print(" error on sending")


def forwardMsgToWebApp(msg):
    try:
        client_webapp.sendto(msg)
        msg.clearData()
     except:
        print(" error on sending")

    # EXEMPLE HOW TO SEND AN OSC MESSAGE
    # oscmsg = OSC.OSCMessage()
    # oscmsg.setAddress("/startup")
    # oscmsg.append('HELLO')
    # c.send(oscmsg)

def powerOff():

    time.sleep(5)
    print("========= POWER OFF ======")
    os.chdir("/home/pi/Documents/radiologic2/script/")
    subprocess.call(['./shutdown.sh'])

def reboot():

    time.sleep(5)
    print("========= POWER OFF ======")
    os.chdir("/home/pi/Documents/radiologic2/script/")
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
    os.chdir("/home/pi/Documents/radiologic2/script/")
    subprocess.call(["./quit.sh"])
    print("======== ALL APP QUITTED ====")

def update_of():
    print("========= UPDATE OF APP ======")
    os.chdir("/home/pi/Documents/openFrameworks/apps/universalMediaPlayer/script")
    subprocess.call(["./update.sh"])
    print("========= OF APP UPDATED ======")

def update_of():
    print("========= UPDATE RADIOLOGIC2 ======")
    os.chdir("/home/pi/Documents/radiologic2/script/")
    subprocess.call(["./update.sh"])
    print("========= RADIOLOGIC2 then reboot ======")

def start_app():
    
    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        print("========= START OF_APP ======")
        os.chdir("/home/pi/Documents/openFrameworks/apps/universalMediaPlayer/of_universalMediaPlayer/bin")
	cmd = ["./of_universalMediaPlayer"]
        subprocess.Popen(cmd)
        print("========= START OF_webapp =======")
        os.chdir("/home/pi/Documents/openFrameworks/apps/universalMediaPlayer/node")
        cmd = ["node", "."]
	subprocess.Popen(cmd)
        print("========= START RADIOLOGIC2 webapp =======")
        os.chdir("/home/pi/Documents/radiologic2/webapp")
        subprocess.Popen(["node", "."])
        #print("========= START VERMUTH ======")
        #os.chdir("/home/pi/vermouth")
        #subprocess.call(["node", "."])


        ########################
        # exemple using POPEN : which is a non blocking process
        # cmd = ["pd",  "-nogui",  "-jack",  "/home/pi/lucibox/machines/"+str(machine)+"/nogui.pd"]
        # subprocess.Popen(cmd)
        # print("======== PUREDATA STARTED ====")
        # print("========= START OPEN STAGE CONTROL ======")
        # cmd = ["node",  "/home/pi/open-stage-control/app",  "-l",  "/home/pi/lucibox/machines/"+str(machine)+"/osc.json", "-s", "127.0.0.1:9999", "-o", "9998"]
        # subprocess.Popen(cmd)
        # print("========= OPEN STAGE CONTROL STARTED ======")

def main():
        
        # OSC SERVER      
        myip = get_ip()
        #myip = "127.0.0.1"
        print("IP adress is : "+myip)
        try:
            server = SimpleServer((myip, 12354)) 
        except:
            print(" ERROR : creating server") 
        print("server created") 
        try:
            st = threading.Thread(target = server.serve_forever) 
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
        client_of.connect( ('127.0.0.1', 12343))

        # OSC CLIENT : OPENFRAMEWORKS WEB APP
        global client_ofWeb
        client_ofWeb = OSCClient()
        client_ofWeb.connect( ('127.0.0.1', 12342))

        # OSC CLIENT : WEBAPP APP ( the one on this repo)
        global client_webapp
        client_webapp = OSCClient()
        client_webapp.connect( ('127.0.0.1', 12345))

        # OSC CLIENT : VERMUTH APP
        #global client_webapp
        #client_webapp = OSCClient()
        #client_webapp.connect( ('127.0.0.1', 12346))

        #START ON BOOT
        start_app() 

        # MAIN LOOP 
        global runningApp
        runningApp = True

        
        print(" ===== STARTING MAIN LOOP ====" )
        while runningApp:
            # This is the main loop
            # Do something here
            try:
                time.sleep(1)
            except:
                print("User attempt to close programm")
                runningApp = False
        
        #CLOSING THREAD AND SERVER
        print(" Ending programme") 
        server.running = False
        print(" Join thread") 
        st.join()
        server.close()
        print(" This is probably the end") 



if __name__ == "__main__":
    main()
