# Copyright 2023 Bardia Moshiri
# SPDX-License-Identifier: GPL-3.0-or-later
import re
import sys
import time
import logging
import threading
import subprocess
from pydbus import SessionBus
from collections import defaultdict
from tools import helpers
from tools import config
from tools.helpers import ipc
from tools.interfaces import IPlatform
from tools.actions import app_manager
from tools.interfaces import INotification
from pydbus import SessionBus

running = False
loop_thread = None

def on_action_invoked(notification, action_key):
    if action_key == 'open':
        app_manager.showFullUI(args)

def get_app_name_dict():
    '''
    This function returns a dictionary of package names and app names
    '''
    args = None
    app_name_dict = {}
    try:
        # Initialize arguments
        args = helpers.arguments()
        args.cache = {}
        args.work = config.defaults["work"]
        args.config = args.work + "/waydroid.cfg"
        args.log = args.work + "/waydroid.log"
        args.sudo_timer = True
        args.timeout = 1800

        # Initialize DBus services
        ipc.DBusSessionService()
        # Initialize container manager which is needed to get session state
        cm = ipc.DBusContainerService()
        session = cm.GetSession()
        # Unfreeze container if it is frozen
        if session["state"] == "FROZEN":
            cm.Unfreeze()

        platformService = IPlatform.get_service(args)
        if platformService:
            appsList = platformService.getAppsInfo()
            for app in appsList:
                package_name = app["packageName"]
                app_name = app["name"]
                app_name_dict[package_name] = app_name
        else:
            logging.error("Failed to access IPlatform service")

        if session["state"] == "FROZEN":
            cm.Freeze()

    except dbus.DBusException:
        logging.error("WayDroid session is stopped")

    return app_name_dict

def get_notifs(prev_notifs):
    global running
    notif_counts = defaultdict(int)

    logging.info("Starting get notification service")

    while running:
        command = [
            "lxc-attach", "-P", "/var/lib/waydroid/lxc",
            "-n", "waydroid", "--clear-env", "--", "/system/bin/sh", "-c", "dumpsys notification"
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stderr:
            print(f"Error: {stderr.decode()}")
            continue

        stdout = stdout.decode()
        filtered_output = re.findall(r"NotificationRecord.*", stdout)
        app_name_dict = get_app_name_dict()

        for line in filtered_output:
            fields = line.split("|")

            if len(fields) > 1:
                notif_name = fields[1].strip()
                if notif_name in app_name_dict:
                    notif_counts[notif_name] += 1

        for package_name, count in notif_counts.items():
            app_name = app_name_dict.get(package_name, package_name)
            prev_count = prev_notifs.get(package_name, 0)

            if count > prev_count:
                print(f"You have {count} notifications from {app_name}")
                # send_notification(app_name, count)
                interface = INotification('id.waydro.Notification')
                interface.NewMessage(app_name, count)

        prev_notifs = notif_counts.copy()
        time.sleep(3)

def start(args):
    print("starting notification manager")
    global running
    global loop_thread

    running = True
    loop_thread = threading.Thread(target=get_notifs, args=({},))
    loop_thread.start()

def stop():
    global running
    global loop_thread

    running = False
    if loop_thread is not None:
        loop_thread.join()

def restart(args):
    stop()
    start(args)

def status():
    global running
    return running