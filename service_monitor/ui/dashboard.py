import tkinter as tk
from tkinter import ttk

class Dashboard:
    def __init__(self, services, settings_manager):
        self.services = services
        self.settings_manager = settings_manager
        self.root = tk.Toplevel()
        self.root.title("Service Dashboard")

        self.service_status_labels = {}

        self.restore_window_position("dashboard")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_widgets()
        self.update_status()

    def create_widgets(self):
        for service in self.services:
            self.add_service_widget(service)

    def add_service_widget(self, service):
        if service.name not in self.service_status_labels:
            frame = ttk.Frame(self.root)
            frame.pack(fill=tk.X, pady=5)

            name_label = ttk.Label(frame, text=service.name, width=20)
            name_label.pack(side=tk.LEFT, padx=5)

            status_label = ttk.Label(frame, text="Checking...", width=20)
            status_label.pack(side=tk.LEFT, padx=5)

            self.service_status_labels[service.name] = status_label

    def update_status(self):
        for service in self.services:
            status_label = self.service_status_labels[service.name]
            status_label.config(text=service.status, foreground="green" if service.status == "Online" else "red")

        self.root.after(1000, self.update_status)

    def show(self):
        self.root.mainloop()

    def restore_window_position(self, window_name):
        position = self.settings_manager.get_window_position(window_name)
        if position:
            x, y = position.split('+')[1], position.split('+')[2]
            self.root.geometry(f"+{x}+{y}")

    def save_window_position(self, window_name):
        position = self.root.geometry()
        self.settings_manager.set_window_position(window_name, position)

    def on_closing(self):
        self.save_window_position("dashboard")
        self.root.destroy()
