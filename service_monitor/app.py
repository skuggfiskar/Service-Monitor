import tkinter as tk
from ui.service_monitor_app import ServiceMonitorApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceMonitorApp(root)
    root.mainloop()
