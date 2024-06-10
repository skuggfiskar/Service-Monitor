import tkinter as tk
from tkinter import ttk, messagebox
from service import create_service
from profiles.profile_manager import ProfileManager
from settings_manager import SettingsManager

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
        messagebox.showinfo("Profile Loaded", f"Loaded profile: {profile_name}")

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
                'Host': service.host
            }
            if service.service_type == 'MongoDB':
                data['DB'] = service.db
            elif service.service_type == 'WebApp':
                data['Healthcheck'] = service.healthcheck
                data['Response'] = service.response_type
            profile_data.append(data)

        self.profile_manager.save_profile(self.current_profile, profile_data)
        messagebox.showinfo("Profile Saved", f"Profile {self.current_profile} saved successfully!")

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

class AddServiceDialog:
    def __init__(self, parent, settings_manager):
        self.top = tk.Toplevel(parent.root)
        self.top.title("Add Service")

        self.settings_manager = settings_manager
        self.restore_window_position("add_service_window")
        self.top.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.parent = parent

        self.name_label = ttk.Label(self.top, text="Name:")
        self.name_label.pack()
        self.name_entry = ttk.Entry(self.top)
        self.name_entry.pack()

        self.type_label = ttk.Label(self.top, text="Type:")
        self.type_label.pack()
        self.type_combo = ttk.Combobox(self.top, values=["MongoDB", "WebApp"])
        self.type_combo.pack()
        self.type_combo.bind("<<ComboboxSelected>>", self.update_fields)

        self.host_label = ttk.Label(self.top, text="Host:")
        self.host_label.pack()
        self.host_entry = ttk.Entry(self.top)
        self.host_entry.pack()

        self.db_label = ttk.Label(self.top, text="DB:")
        self.db_entry = ttk.Entry(self.top)

        self.healthcheck_label = ttk.Label(self.top, text="Healthcheck:")
        self.healthcheck_entry = ttk.Entry(self.top)

        self.response_label = ttk.Label(self.top, text="Response:")
        self.response_combo = ttk.Combobox(self.top, values=["JSON", "TEXT"])

        self.add_button = ttk.Button(self.top, text="Add", command=self.add_service)
        self.add_button.pack()

    def update_fields(self, event):
        service_type = self.type_combo.get()
        if service_type == "MongoDB":
            self.db_label.pack()
            self.db_entry.pack()
            self.healthcheck_label.pack_forget()
            self.healthcheck_entry.pack_forget()
            self.response_label.pack_forget()
            self.response_combo.pack_forget()
        elif service_type == "WebApp":
            self.db_label.pack_forget()
            self.db_entry.pack_forget()
            self.healthcheck_label.pack()
            self.healthcheck_entry.pack()
            self.response_label.pack()
            self.response_combo.pack()

    def add_service(self):
        service_data = {
            'Name': self.name_entry.get(),
            'Type': self.type_combo.get(),
            'Host': self.host_entry.get()
        }
        if service_data['Type'] == "MongoDB":
            service_data['DB'] = self.db_entry.get()
        elif service_data['Type'] == "WebApp":
            service_data['Healthcheck'] = self.healthcheck_entry.get()
            service_data['Response'] = self.response_combo.get()

        service = create_service(service_data)
        self.parent.services.append(service)
        self.top.destroy()

    def restore_window_position(self, window_name):
        position = self.settings_manager.get_window_position(window_name)
        if position:
            x, y = position.split('+')[1], position.split('+')[2]
            self.top.geometry(f"+{x}+{y}")

    def save_window_position(self, window_name):
        position = self.top.geometry()
        self.settings_manager.set_window_position(window_name, position)

    def on_closing(self):
        self.save_window_position("add_service_window")
        self.top.destroy()

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
            if service.name not in self.service_status_labels:
                self.add_service_widget(service)

            status = service.check_status()
            status_label = self.service_status_labels[service.name]
            status_label.config(text=status, foreground="green" if status == "Online" else "red")

        self.root.after(10000, self.update_status)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceMonitorApp(root)
    root.mainloop()
