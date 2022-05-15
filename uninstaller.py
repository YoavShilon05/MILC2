import os
import winreg
import shutil

home = os.path.expandvars("%appdata%/MILC2")

def delete_subkeys(key0, current_key):
    # stolen from https://stackoverflow.com/questions/38205784/python-how-to-delete-registry-key-and-subkeys-from-hklm-getting-error-5
    with (winreg.OpenKey(key0, current_key, 0, winreg.KEY_ALL_ACCESS)) as key:
        info_key = winreg.QueryInfoKey(key)
        for x in range(info_key[0]):
            sub_key = winreg.EnumKey(key, 0)
            try:
                winreg.DeleteKey(key, sub_key)
            except OSError:
                delete_subkeys(key0, "\\".join([current_key, sub_key]))


shutil.rmtree(home)

