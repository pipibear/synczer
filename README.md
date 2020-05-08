# Description
This is a configured data synchronization tool. It is written based on Qt5 in Python language and used for the synchronization tool between massive data. It supports MySQL and Elasticsearch. You can monitor your data synchronization progress through the visual interface. It supports full and incremental data synchronization. Through the configuration file, you can easily customize the data synchronization between different data sources.

![screenshot](https://github.com/pipibear/synczer/blob/master/screenshot.png)

# Requirements
- python3.7+
- pyinstaller3.5+
- pyqt5.13+

you also need to download [mysql-importer-server](https://github.com/pipibear/mysql-importer-server) to export sql file quickly.

# Quick Start
run `python main.py` on command line

you can also view the ./config.ini for details

# Compile
- windows
  - run ./build.bat on command line
- mac
  - run ./build.sh on terminal shell

