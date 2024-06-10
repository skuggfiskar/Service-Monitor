import tkinter as tk
from tkinter import ttk
from service import create_service, MongoDBService, WebAppService

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

        self.response_frame = ttk.LabelFrame(self.top, text="Response")
        self.response_frame.pack(fill="both", expand="yes", padx=10, pady=10)

        self.response_type_label = ttk.Label(self.response_frame, text="Type:")
        self.response_type_label.pack()
        self.response_type_combo = ttk.Combobox(self.response_frame, values=["JSON", "TEXT"])
        self.response_type_combo.pack()

        self.expected_status_code_label = ttk.Label(self.response_frame, text="Expected Status Code:")
        self.expected_status_code_label.pack()
        self.expected_status_code_entry = ttk.Entry(self.response_frame)
        self.expected_status_code_entry.pack()

        self.expected_content_label = ttk.Label(self.response_frame, text="Expected Content:")
        self.expected_content_label.pack()
        self.expected_content_entry = ttk.Entry(self.response_frame)
        self.expected_content_entry.pack()

        self.interval_label = ttk.Label(self.top, text="Refresh Interval (seconds):")
        self.interval_label.pack()
        self.interval_entry = ttk.Entry(self.top)
        self.interval_entry.pack()

        self.add_button = ttk.Button(self.top, text="Add", command=self.add_service)
        self.add_button.pack()

    def update_fields(self, event):
        service_type = self.type_combo.get()
        if service_type == "MongoDB":
            self.db_label.pack()
            self.db_entry.pack()
            self.healthcheck_label.pack_forget()
            self.healthcheck_entry.pack_forget()
            self.response_frame.pack_forget()
        elif service_type == "WebApp":
            self.db_label.pack_forget()
            self.db_entry.pack_forget()
            self.healthcheck_label.pack()
            self.healthcheck_entry.pack()
            self.response_frame.pack(fill="both", expand="yes", padx=10, pady=10)

    def add_service(self):
        interval = int(self.interval_entry.get()) if self.interval_entry.get() else 10
        service_data = {
            'Name': self.name_entry.get(),
            'Type': self.type_combo.get(),
            'Host': self.host_entry.get(),
            'Interval': interval
        }
        if service_data['Type'] == "MongoDB":
            service_data['DB'] = self.db_entry.get()
            service = MongoDBService(service_data['Name'], service_data['Host'], service_data['DB'], interval)
        elif service_data['Type'] == "WebApp":
            service_data['Healthcheck'] = self.healthcheck_entry.get()
            service_data['Response'] = {
                'Type': self.response_type_combo.get(),
                'ExpectedStatusCode': int(self.expected_status_code_entry.get()) if self.expected_status_code_entry.get() else None,
                'ExpectedContent': self.expected_content_entry.get() if self.expected_content_entry.get() else None
            }
            service = WebAppService(service_data['Name'], service_data['Host'], service_data['Healthcheck'], service_data['Response'], interval)

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
