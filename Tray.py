import logging
import os
import sys

import pystray
from pystray import MenuItem as Item
from pystray import Menu
from PIL import Image
from Settings import icon_path, root, settings_path, executable_path, log_path
from Client import Client
import shutil


class Tray():

    def __init__(self):
        self.client = Client()
        self.update_users()

        self.tray = pystray.Icon("MILC", Image.open(icon_path), "Hi mom, please press this icon to open up the "
                                                                "options menu <3",
                                 Menu(Item("Update user list", self.update_users),
                                      Item("Open root folder", self.open_root),
                                      Item("Settings", self.settings),
                                      Item("Check for updates", self.install_updates),
                                      Item("Restart", self.restart),
                                      Item("Leave Exit", self.quit)))

    def __enter__(self): return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info(f"Exiting tray, turning off client and icon.")
        self.client.__exit__(exc_type, exc_val, exc_tb)
        self.tray.stop()

    def update_users(self):
        Client.update_users()

    def open_root(self):
        logging.info(f"Opening root")
        os.system(f"explorer {root}")

    def settings(self):
        logging.info(f"Opening settings")
        os.system(f"start {settings_path}")

    def install_updates(self):
        up_to_date = Client.check_for_updates()
        if not up_to_date:
            logging.info("Client not up to date! installing updates, copying logs and quitting")

            # copy old log to new file
            shutil.copyfile(log_path, log_path.replace("log.log", "log_old.log"))

            Client.install_updates()
            self.quit()

    def restart(self):
        logging.info(f"Restarting")

        # copy old log to new file
        shutil.copyfile(log_path, log_path.replace("log.log", "log_old.log"))

        os.execv(executable_path, sys.argv)

    def quit(self):
        logging.info(f"Quitting")
        sys.exit(0)

    def run(self):
        logging.info(f"Starting client")
        self.client.listen()

    def show(self):
        logging.info(f"Showing tray")
        self.tray.run()
