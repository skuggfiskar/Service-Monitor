import tkinter as tk
from tkinter import ttk, messagebox
from profiles.profile_manager import ProfileManager
from settings_manager import SettingsManager
from dialogs.add_service_dialog import AddServiceDialog
from ui.dashboard import Dashboard
from service import create_service

class ServiceMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Service Monitor")

        self.profile_manager = ProfileManager()
        self.settings_manager = SettingsManager()
        self.services = []
        self.current_profile = None
        self.dashboard = None

        self.restore_window_position("main_window")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_widgets()

    def create_widgets(self):
        self.profile_label = ttk.Label(self.root, text="Select Profile:")
        self.profile_label.pack()

        self.profile_combo = ttk.Combobox(self.root, values=self.profile_manager.get_profiles())
        self.profile_combo.pack()
        self.profile_combo.bind("<<ComboboxSelected>>", self.load_profile)

        self.add_service_button = ttk.Button(self.root, text="Add Service", command=self.add_service)
        self.add_service_button.pack()

        self.service_frame = ttk.Frame(self.root)
        self.service_frame.pack()

        self.status_button = ttk.Button(self.root, text="Check Status", command=self.open_dashboard)
        self.status_button.pack()

        self.save_button = ttk.Button(self.root, text="Save Profile", command=self.save_profile)
        self.save_button.pack()

    def restore_window_position(self, window_name):
        position = self.settings_manager.get_window_position(window_name)
        if position:
            self.root.geometry(position)

    def save_window_position(self, window_name):
        position = self.root.geometry()
        self.settings_manager.set_window_position(window_name, position)

    def load_profile(self, event):
        profile_name = self.profile_combo.get()
        self.current_profile = profile_name
        profile_data = self.profile_manager.load_profile(profile_name)
        self.services = [create_service(data) for data in profile_data]
        # messagebox.showinfo("Profile Loaded", f"Loaded profile: {profile_name}")

    def add_service(self):
        AddServiceDialog(self, self.settings_manager)

    def save_profile(self):
        if not self.current_profile:
            profile_name = self.profile_combo.get()
            if not profile_name:
                messagebox.showerror("Error", "No profile selected to save.")
                return
            # New profile
            self.current_profile = profile_name

        profile_data = []
        for service in self.services:
            data = {
                'Name': service.name,
                'Type': service.service_type,
                'Host': service.host,
                'Interval': service.interval
            }
            if service.service_type == 'MongoDB':
                data['DB'] = service.db
            elif service.service_type == 'WebApp':
                data['Healthcheck'] = service.healthcheck
                data['Response'] = service.response
            profile_data.append(data)

        self.profile_manager.save_profile(self.current_profile, profile_data)
        # messagebox.showinfo("Profile Saved", f"Profile {self.current_profile} saved successfully!")

    def open_dashboard(self):
        if self.dashboard is None or not self.dashboard.root.winfo_exists():
            self.dashboard = Dashboard(self.services, self.settings_manager)
            self.dashboard.show()
        else:
            self.dashboard.services = self.services
            self.dashboard.update_status()

    def on_closing(self):
        self.save_window_position("main_window")
        if self.dashboard and self.dashboard.root.winfo_exists():
            self.dashboard.save_window_position("dashboard")
        self.root.destroy()
