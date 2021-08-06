#!/bin/bash

lxc-stop -n waydroid -k
/usr/share/waydroid/anbox-net.sh stop
kill `pidof anbox-sensord`
