import sys
import logging
import Sender
from Tray import Tray
from Settings import log_path

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', filename=log_path, filemode='w')


if __name__ == "__main__":

    if len(sys.argv) < 2:
        raise SyntaxError("Beware! The file you have just ran relies and must be run with an argument parameter. "
                          "running it without one will surely cause it to fail critically. Please take the necessary "
                          "steps to make sure such accidents will not take place next time.")

    match (sys.argv[1]):
        case "listen":
            with Tray() as tray:
                tray.run()


        case "send":
            target = sys.argv[2]
            path = sys.argv[3]

            logging.info(f"Sending {path} to {target}")
            with Sender.Sender() as sender:
                sender.send(path, target)

        case _:
            raise ValueError("Beware! The Value entered for the above argument while running this very program has resulted "
                            "in a fatal error! please take the necessary steps to make sure this type of argument won't be "
                            "passed to this program any more.")
