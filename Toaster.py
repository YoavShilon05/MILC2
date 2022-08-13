import os

from win10toast_click import ToastNotifier
from Settings import icon_path, root

toaster = ToastNotifier()

def notify(msg, on_click=None):
    toaster.show_toast("MILC", msg, icon_path=icon_path, threaded=True, callback_on_click=on_click)

def open_explorer_on_click(path):
    dst = root + '\\' + os.path.dirname(path).replace('//', '/').replace('/', '\\')
    def foo():
        os.system(f"explorer {dst}")
    return foo