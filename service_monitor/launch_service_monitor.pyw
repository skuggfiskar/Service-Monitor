import tkinter as tk
from ui.service_monitor_app import ServiceMonitorApp

root = tk.Tk()
app = ServiceMonitorApp(root)
root.mainloop()
print(__name__)
