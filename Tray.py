import logging
import os
import subprocess
import sys
import threading

import pystray
from pystray import MenuItem as Item
from pystray import Menu
from PIL import Image
from Settings import icon_path, root, settings_path, executable_path, log_path, updater_path, update_users_path
from Client import Client
import shutil
from updater import check_for_updates
from Toaster import notify

class Tray():

    def __init__(self):
        logging.info("Initiating Tray...")
        self.client = Client()
        logging.info("Updating users through Tray...")
        self.update_users()

        self.tray = pystray.Icon("MILC", Image.open(icon_path), "Hi mom, please press this icon to open up the "
                                                                "options menu <3",
                                 Menu(Item("Open root folder", self.open_root),
                                      Item("Settings", self.settings),
                                      Item("Check for updates", self.install_updates),
                                      Item("Update user list", self.update_users),
                                      Item("Restart", self.restart),
                                      Item("Leave Exit", self.quit)))

    def __enter__(self): return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info(f"Exiting tray, turning off client and icon.")
        self.client.__exit__(exc_type, exc_val, exc_tb)
        self.tray.stop()

    def update_users(self):
        subprocess.run(update_users_path)

    def open_root(self):
        logging.info(f"Opening root folder, {root=}")
        os.system(f"explorer {root}")

    def settings(self):
        logging.info(f"Opening settings, {settings_path=}")
        os.system(f"start {settings_path}")

    def install_updates(self):
        update_available, version = check_for_updates()
        if update_available:
            logging.info("Client not up to date! installing updates, copying logs and quitting")
            notify("Installing updates...")

            # copy old log to new file
            shutil.copyfile(log_path, log_path.replace("log.log", "log_old.log"))
            logging.info("Rolled logs, quitting...")
            os.execv(updater_path, [updater_path, version])

        else:
            notify("your MILC2 program is up to date!")

    def restart(self):
        logging.info(f"Restarting by user request...")

        # copy old log to new file
        shutil.copyfile(log_path, log_path.replace("log.log", "log_old.log"))
        logging.info("Rolled logs")
        self.tray.stop()

        os.execv(executable_path, sys.argv)

    def quit(self):
        logging.info(f"Quitting by user request...")

        # copy old log to new file
        shutil.copyfile(log_path, log_path.replace("log.log", "log_old.log"))
        logging.info("Rolled logs")

        self.tray.stop()

        # what the actual fuck is that
        os._exit(0)

    def run(self):
        logging.info(f"Starting client...")
        self.client.listen()

    def show(self):
        logging.info(f"Showing tray...")
        threading.Thread(target=self.tray.run, daemon=True).start()
