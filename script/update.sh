#!/bin/sh
cd /home/pi/Documents/radiologic2/
echo "GIT PULL"
git pull
#git reset --soft HEAD
echo "BUILD OF WEB APP"
cd webapp/public
npm run build
echo "UPDATE IS DONE"

