import tkinter as tk
from tkinter import ttk, messagebox
from service import create_service
from profiles.profile_manager import ProfileManager

class ServiceMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Service Monitor")

        self.profile_manager = ProfileManager()
        self.services = []

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

        self.status_button = ttk.Button(self.root, text="Check Status", command=self.check_status)
        self.status_button.pack()

    def load_profile(self, event):
        profile_name = self.profile_combo.get()
        profile_data = self.profile_manager.load_profile(profile_name)
        self.services = [create_service(data) for data in profile_data]

    def add_service(self):
        AddServiceDialog(self)

    def check_status(self):
        for service in self.services:
            status = service.check_status()
            messagebox.showinfo("Service Status", f"{service.name}: {status}")

class AddServiceDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent.root)
        self.top.title("Add Service")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceMonitorApp(root)
    root.mainloop()
