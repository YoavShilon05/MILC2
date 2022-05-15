import logging
import os
import sys
from urllib.request import urlopen, urlretrieve
from Settings import version_path, executable_path
from Toaster import notify


def check_for_updates() -> (bool, str):
    """
    checks if any updates are available
    """
    latest = urlopen("https://github.com/YoavShilon05/MILC2/releases/latest").geturl()
    ver = latest.split('/')[-1]
    with open(version_path, 'r') as f:
        if f.read() != ver:
            logging.info(f"Update {ver} available")
            return True, ver
        return False, ""

def main():
    # call with Updater.exe <version>
    if len(sys.argv) != 1:
        raise ValueError(
            "Beware! The Value entered for the above argument while running this very program has resulted "
            "in a fatal error! please take the necessary steps to make sure this type of argument won't be "
            "passed to this program any more.")

    logging.info("Installing updates")

    urlretrieve(f"https://github.com/YoavShilon05/MILC2/releases/tag/{sys.argv[1]}/download/MILC2.exe", executable_path)

    with open(version_path, 'w') as f:
        f.write(sys.argv[1])

    notify("updates for MILC2 installed!")

    os.execv(executable_path, ["listen", "nocheck"])

if __name__ == "__main__":
    main()
