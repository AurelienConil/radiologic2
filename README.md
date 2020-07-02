# radiologic2
 update architecture of radiologic project

# main.py
This is python daemon that start on boot through a service.
This is the only that start on boot
Then all the others app are started inside this programm when it starts
This programm has the ability to start and stop all the other programm

# conf json files
UserSettings.json and datajson.json will be created on the first run if non existent
then, git update mechanism wont override it

no need to edit UserSettings.json, it's synced with web UI
for datajson.json please look at the default in webapp/public/public/datajson.json

meaning of datajson params :
 * 

# modifying remotly
one can download at <ip_address>:3000/datajson.json
one can upload going to the <ip_address>:3000/json


# script
all script need to be switch manually in sudo owner
sudo chmod 777 shutdown.sh
sudo chmod 777 autostart.sh etc