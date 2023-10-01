# Copyright 2023 Bardia Moshiri
# SPDX-License-Identifier: GPL-3.0-or-later
import re
import sys
import time
import logging
import threading
import subprocess
from pydbus import SessionBus
from gi.repository import GLib
from collections import defaultdict
from tools import helpers
from tools import config
from tools.helpers import ipc
from tools.interfaces import IPlatform
from tools.actions import app_manager

main_loop = None
running = False
loop_thread = None

def stop_main_loop():
    global main_loop
    if main_loop:
        main_loop.quit()

    return False

def on_action_invoked(notification, action_key):
    if action_key == 'open':
        app_manager.showFullUI(args)

def send_notification(app_name, notif_amount):
    global main_loop

    bus = SessionBus()
    notifications = bus.get('.Notifications')
    notifications.ActionInvoked.connect(on_action_invoked)

    notifications.Notify(
        "Waydroid",
        0,
        "/usr/share/icons/hicolor/512x512/apps/waydroid.png",
        app_name,
        f"You have {notif_amount} notifications",
        ['default', 'Open', 'open', 'Open'],
        {'urgency': GLib.Variant('y', 1)},
        5000
    )

    GLib.timeout_add_seconds(3, stop_main_loop)

    main_loop = GLib.MainLoop()
    main_loop.run()

def get_app_name_dict():
    args = None
    app_name_dict = {}
    try:
        args = helpers.arguments()
        args.cache = {}
        args.work = config.defaults["work"]
        args.config = args.work + "/waydroid.cfg"
        args.log = args.work + "/waydroid.log"
        args.sudo_timer = True
        args.timeout = 1800

        ipc.DBusSessionService()
        cm = ipc.DBusContainerService()
        session = cm.GetSession()
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

    while running:
        command = [
            "sudo", "lxc-attach", "-P", "/var/lib/waydroid/lxc",
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
                send_notification(app_name, count)

        prev_notifs = notif_counts.copy()
        time.sleep(3)

def start(args):
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
