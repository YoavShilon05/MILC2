import logging
import os
import sys
from urllib.request import urlopen, urlretrieve
from Settings import version_path, executable_path, log_path
from Toaster import notify


def check_for_updates() -> (bool, str):
    """
    checks if any updates are available
    """
    logging.info("Checking for updates...")
    latest = urlopen("https://github.com/YoavShilon05/MILC2/releases/latest").geturl()
    latest_ver = latest.split('/')[-1]
    logging.info(f"Latest version: {latest_ver}")
    with open(version_path, 'r') as f:
        current_ver = f.read()
        logging.info(f"Current MILC2 version: {current_ver}")
        if current_ver != latest_ver:
            logging.info(f"MILC2 Update available")
            return True, latest_ver

        logging.info(f"MILC2 is up to date")
        return False, ""

def main():
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', filename=log_path, filemode='a',
                        level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())  # add console output

    # call with Updater.exe <version>
    if len(sys.argv) != 2:
        raise ValueError(
            "Beware! The Value entered for the above argument while running this very program has resulted "
            "in a fatal error! please take the necessary steps to make sure this type of argument won't be "
            f"passed to this program any more. Arguments got: {sys.argv}")

    logging.info("Installing updates")
    notify("Installing updates")

    latest = urlopen("https://github.com/YoavShilon05/MILC2/releases/latest").geturl()
    latest = latest.replace("/tag/", "/download/")
    urlretrieve(f"{latest}/MILC2.exe", executable_path)

    logging.info("Finished installing updates.")
    with open(version_path, 'w') as f:
        f.write(sys.argv[1])

    notify("updates for MILC2 installed!")

    os.execv(executable_path, [executable_path, "listen", "nocheck"])

if __name__ == "__main__":
    main()
