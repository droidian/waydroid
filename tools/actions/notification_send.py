import os
import re
import sys
import time
import logging
import threading
import subprocess
from pydbus import SessionBus
from gi.repository import GLib
from tools.actions import app_manager
import asyncio
from dbus_next.aio import MessageBus
from dbus_next import BusType
import dbus.service
import dbus.mainloop.glib
import dbus.exceptions
import dbus.mainloop.glib
import asyncio
from dbus_next.aio import MessageBus
from dbus_next import BusType
import asyncio


main_loop = None
 
def stop_main_loop():
    global main_loop
    if main_loop:
        main_loop.quit()

    return False

def on_action_invoked(notification, action_key):
    if action_key == 'open':
        app_manager.showFullUI(args)


def on_new_message(app_name, count):
    global main_loop
    logging.info(f"Got new message: appname = {app_name} count ={count}")

    # Bus session
    bus = SessionBus()
    # Initialize DBus services
    notifications = bus.get('.Notifications')
    # Connect to action invoked signal
    notifications.ActionInvoked.connect(on_action_invoked)

    notifications.Notify(
        "Waydroid",
        0,
        "/usr/share/icons/hicolor/512x512/apps/waydroid.png",
        app_name,
        f"You have {count} notifications or gey",
        ['default', 'Open', 'open', 'Open'],
        {'urgency': GLib.Variant('y', 1)},
        5000
    )

    GLib.timeout_add_seconds(3, stop_main_loop)

    main_loop = GLib.MainLoop()
    main_loop.run()


async def receive_notification():
    print("receiving notification from waydroid")
    # Connect to the session bus for the current user
    input_bus = await MessageBus(bus_type=BusType.SESSION).connect()

    logging.info("Connected to session bus")

    # get app name and count from input_bus
    introspect = await input_bus.introspect('id.waydro.Notification', '/')

    logging.info("Introspected")
    print("Introspected")
    obj = input_bus.get_proxy_object('id.waydro.Notification', '/', introspect)
    interface = obj.get_interface('id.waydro.Notification')

    interface.on_new_message(on_new_message)


global notification_task
notification_task = None

def start(args):
    print("starting notification_send service")
    global notification_task
    if notification_task:
        logging.info("Notification service is already running")
        return
    notification_task = asyncio.create_task(receive_notification())

def stop():
    global notification_task
    if notification_task:
        notification_task.cancel()
        stop_main_loop()
    