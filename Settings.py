import configparser
import os

config = configparser.ConfigParser()
settings_path = os.path.expandvars("%appdata%/MILC2/settings.ini")
icon_path = os.path.expandvars("%appdata%/MILC2/MILC2.ico")
version_path = os.path.expandvars("%appdata%/MILC2/version.txt")
executable_path = os.path.expandvars("%appdata%/MILC2/MILC2.exe")
log_path = os.path.expandvars("%appdata%/MILC2/log.log")
updater_path = os.path.expandvars("%appdata%/MILC2/Updater.exe")
update_users_path = os.path.expandvars("%appdata%/MILC2/UpdateUsers.exe")
# settings_path = os.path.expandvars("Settings.ini")
config.read(settings_path)

ip = config["Settings"]["IP"]
root = os.path.normpath(config["Settings"]["Root"])
username = config["Settings"]["Username"]
