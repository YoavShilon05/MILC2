import winreg
from AssiNet import *

def update_users():
    logging.info("Updating users")

    def delete_subkeys(key0, current_key: str):
        # stolen from https://stackoverflow.com/questions/38205784/python-how-to-delete-registry-key-and-subkeys-from-hklm-getting-error-5
        logging.info(f"attempting to open key {current_key} (to delete it)")
        with (winreg.OpenKey(key0, current_key, 0, winreg.KEY_ALL_ACCESS)) as key:
            logging.info(f"successfully opened key {current_key}")
            info_key = winreg.QueryInfoKey(key)
            for x in range(info_key[0]):
                sub_key = winreg.EnumKey(key, 0)
                try:
                    logging.info(f"attempting to delete key {sub_key}")
                    winreg.DeleteKey(key, sub_key)
                    logging.info(f"successfully deleted key {sub_key}")
                except OSError:
                    new_key = "\\".join([current_key, sub_key])
                    logging.info(f"recursing for unknown reasons with {new_key}")
                    delete_subkeys(key0, new_key)

    def add(path, u, arg='%1'):
        logging.info(rf"attempting to open key '{path}\shell\MILC2\shell\SendTo{u}' (to add new stuff to it)")
        with (winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{path}\shell\MILC2\shell\SendTo{u}")) as key:
            logging.info(f"successfully opened key '{path}\shell\MILC2\shell\SendTo{u}'")
            winreg.SetValue(key, "", winreg.REG_SZ, f"Send to {u}")
            winreg.SetValueEx(key, "Icon", None, winreg.REG_EXPAND_SZ, rf"%appdata%\MILC2\MILC2.ico")
            logging.info(f"successfully added context menu item and icon to {path}")
        logging.info(rf"attempting to open key '{path}\shell\MILC2\shell\SendTo{u}\command' (to add new stuff to it)")
        with (winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{path}\shell\MILC2\shell\SendTo{u}\command")) as key:
            logging.info(rf"successfully opened key '{path}\shell\MILC2\shell\SendTo{u}\command'")
            winreg.SetValueEx(key, "", None, winreg.REG_EXPAND_SZ,
                              f'%appdata%\MILC2\MILC2.exe "send" "{u}" "{arg}"')
            logging.info(rf"successfully made context menu item launch MILC2 in path {path}")

    def get_users():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as getter:
            getter.connect((ip, PORT))
            send(getter, b"GET_USERS")
            return pickle.loads(recv(getter))

    # logging.info("deleting existing users")
    # delete_subkeys(winreg.HKEY_CLASSES_ROOT, r"*\shell\MILC2\shell")
    # delete_subkeys(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\MILC2\shell")
    # delete_subkeys(winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\MILC2\shell")
    # logging.info("finished deleting existing users")

    logging.info("starting to add the new users to the context menu")
    for u in get_users():
        logging.info(f"adding {u} to the context menu")
        add("*", u)
        add("Directory", u)
        add("Directory\\Background", u, '%w')
        logging.info(f"done adding {u} to the context menu")
