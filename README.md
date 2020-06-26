# radiologic2
 update architecture of radiologic project

# main.py
This is python daemon that start on boot through a service.
This is the only that start on boot
Then all the others app are started inside this programm when it starts
This programm has the ability to start and stop all the other programm


# script
all script need to be switch manually in sudo owner
sudo chmod 777 shutdown.sh
sudo chmod 777 autostart.sh etc