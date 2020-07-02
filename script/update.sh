#!/bin/sh
cd /home/pi/Documents/radiologic2/
echo "GIT PULL"
git pull
#git reset --soft HEAD
echo "BUILD OF WEB APP"

cd webapp/public
npm i
npm run build

cd ..
npm i
echo "UPDATE IS DONE"

