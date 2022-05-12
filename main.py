import sys

import Sender
from Client import Client

if __name__ == "__main__":

    if len(sys.argv) < 2:
        raise SyntaxError("Beware! The file you have just ran relies and must be run with an argument parameter. "
                          "running it without one will surely cause it to fail critically. Please take the necessary "
                          "steps to make sure such accidents will not take place next time.")

    match (sys.argv[1]):
        case "listen":
            Client.install_updates()
            Client.update_users()
            with Client() as client:
                client.listen()

        case "send":
            target = sys.argv[2]
            path = sys.argv[3]

            with Sender.Sender() as sender:
                sender.send(path, target)

        case _:
            raise ValueError("Beware! The Value entered for the above argument while running this very program has resulted "
                            "in a fatal error! please take the necessary steps to make sure this type of argument won't be "
                            "passed to this program any more.")
