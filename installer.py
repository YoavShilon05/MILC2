import shutil
import winreg
import os.path
from win32com.client import Dispatch
from urllib.request import urlretrieve, urlopen
from inspect import cleandoc

home = os.path.expandvars("%appdata%/MILC2")


def get_input(inp):
    return input(f"{inp}? > ")


def get_valid_input(inp, check, message):
    while check(output := get_input(inp)):
        print(message)
    return output


def create_send_to(path):
    with (winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{path}\shell\MILC2")) as key:
        winreg.SetValueEx(key, "MUIVerb", None, winreg.REG_SZ, "Send to")
        winreg.SetValueEx(key, "subcommands", None, winreg.REG_SZ, "")
    with (winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{path}\shell\MILC2\shell")): ...


def create_item(path, title, arg):
    # winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, rf"{path}\shell\MILC2")
    create_send_to(path)


if __name__ == "__main__":
    print("""
    
     /$$      /$$ /$$$$$$ /$$        /$$$$$$ 
    | $$$    /$$$|_  $$_/| $$       /$$__  $$
    | $$$$  /$$$$  | $$  | $$      | $$  \__/
    | $$ $$/$$ $$  | $$  | $$      | $$      
    | $$  $$$| $$  | $$  | $$      | $$      
    | $$\  $ | $$  | $$  | $$      | $$    $$
    | $$ \/  | $$ /$$$$$$| $$$$$$$$|  $$$$$$/
    |__/     |__/|______/|________/ \______/  2
            Mothers I'd Like to Calm
    
            
    """)
    print("Downloading MILC2...")

    if os.path.isdir(home):
        shutil.rmtree(home)
    os.mkdir(home)

    latest = urlopen("https://github.com/YoavShilon05/MILC2/releases/latest").geturl()
    latest = latest.replace("/tag/", "/download/")
    urlretrieve(f"{latest}/MILC2.exe", f"{home}/MILC2.exe")
    urlretrieve(f"{latest}/MILC2.ico", f"{home}/MILC2.ico")
    urlretrieve(f"{latest}/Updater.exe", f"{home}/Updater.exe")
    urlretrieve(f"{latest}/UpdateUsers.exe", f"{home}/UpdateUsers.exe")
    with open(os.path.expandvars("%appdata%/MILC2/version.txt"), 'w') as f:
        f.write(latest.split('/')[-1])

    print("\nCreating settings...")

    def root_valid(o: str) -> bool:
        return not os.path.isdir(os.path.dirname(o.lstrip('\\/')))

    root = get_valid_input("Root directory", root_valid, "Invalid path").replace('/', '\\').rstrip('\\')
    if not os.path.isdir(root):
        os.mkdir(root)
    name = get_valid_input("Your name", lambda o: ' ' in o, "Spaces in names unsupported")
    ip = get_input("Remote IP")

    with open(f"{home}/settings.ini", 'w') as f:
        f.write(cleandoc(f"""
        [Settings]
        Root={root}
        Username={name}
        IP={ip}
        """))

    print("\nCreating context menu items...")
    create_item("*", "Send file", "%1")
    create_item("Directory", "Send folder", "%1")
    create_item("Directory\\Background", "Send folder", "%w")

    print("\nAdding MILC2 to startup...")
    os.system(r'schtasks /create /sc ONLOGON /tn MILC2 /tr "%appdata%\MILC2\MILC2.exe listen" /rl HIGHEST /f')
    print("\nAdding MILC2 to start menu")
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut("C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\MILC2.lnk")
    shortcut.TargetPath = f"{home}\\MILC2.exe"
    shortcut.IconLocation = f"{home}\\MILC2.ico"
    shortcut.Arguments = "listen"
    shortcut.save()

    print("\n\nDone! Launching MILC2...")
    os.system("schtasks /run /tn MILC2")
