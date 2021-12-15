#!/bin/bash
# /etc/init.d/irrigacao.sh
### BEGIN INIT INFO
# Provides:          irrigacao.sh
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO
export FLASK_ENV=production

cd /home/pi/Desktop/irrigacao
/usr/bin/python3 server.py
