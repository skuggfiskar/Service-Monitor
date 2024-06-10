import json
import os

class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as file:
                return json.load(file)
        return {}

    def save_settings(self):
        with open(self.settings_file, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def get_window_position(self, window_name):
        return self.settings.get(window_name, {}).get("position", None)

    def set_window_position(self, window_name, position):
        if window_name not in self.settings:
            self.settings[window_name] = {}
        self.settings[window_name]["position"] = position
        self.save_settings()
