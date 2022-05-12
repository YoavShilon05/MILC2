from win10toast_click import ToastNotifier
from Settings import icon_path

toaster = ToastNotifier()

def notify(msg, on_click=None):
    toaster.show_toast("MILC", msg, icon_path=icon_path, threaded=True, callback_on_click=on_click)