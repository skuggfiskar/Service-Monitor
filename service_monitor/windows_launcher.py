# Use this script to launch the application on Windows OS
# This script will hide the console window and only show the GUI window
# But it is necessary to have the console window open for Start/Stop commands to work

import tkinter as tk
from ui.service_monitor_app import ServiceMonitorApp
import win32gui, win32con

root = tk.Tk()
app = ServiceMonitorApp(root)

the_program_to_hide = win32gui.GetForegroundWindow()
win32gui.ShowWindow(the_program_to_hide , win32con.SW_HIDE)

root.mainloop()
exit(0)
