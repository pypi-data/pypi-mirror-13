#!/bin/sh
### BEGIN INIT INFO
# Provides:          PiStormsBrowser
# Required-Start:    hostname $local_fs
# Required-Stop:
# Should-Start:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start/stop PiStormsBrowser
# Description:       This script starts/stops PiStormsBrowser.
### END INIT INFO

PATH=/sbin:/usr/sbin:/bin:/usr/bin
. /lib/init/vars.sh

do_start () {
	sudo python /usr/local/lib/python2.7/dist-packages/PiStormsBrowser.py /home/pi/PiStormsprograms & >/dev/null
    chmod a+rw /dev/i2c* > /dev/null 2>&1
	sleep 2
}

do_status () {
	#if [ -e /dev/servoblaster ] ; then
	#	return 0
	#else
	#	return 4
	#fi
    return 0
}

case "$1" in
  start|"")
	do_start
	;;
  restart|reload|force-reload)
	sudo kill -9 `ps -ef | grep PiStormsBrowser.py |grep -v grep| cut -c11-16`
    do_start
	exit 3
	;;
  stop)
	sudo kill -9 `ps -ef | grep PiStormsBrowser.py |grep -v grep| cut -c11-16`
	;;
  status)
	do_status
	exit $?
	;;
  *)
	echo "Usage: PiStormsBrowser [start|stop|status]" >&2
	exit 3
	;;
esac

:
