import json
import os

class ProfileManager:
    def __init__(self, profile_dir="profiles"):
        self.profile_dir = profile_dir
        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir)

    def get_profiles(self):
        return [f.replace('.json', '') for f in os.listdir(self.profile_dir) if f.endswith('.json')]

    def load_profile(self, profile_name):
        profile_path = os.path.join(self.profile_dir, f"{profile_name}.json")
        with open(profile_path, 'r') as file:
            return json.load(file)

    def save_profile(self, profile_name, data):
        profile_path = os.path.join(self.profile_dir, f"{profile_name}.json")
        with open(profile_path, 'w') as file:
            json.dump(data, file, indent=4)
