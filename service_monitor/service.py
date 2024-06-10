import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class Service:
    def __init__(self, name, service_type, host):
        self.name = name
        self.service_type = service_type
        self.host = host

    def check_status(self):
        raise NotImplementedError("Must be implemented by subclasses")

class MongoDBService(Service):
    def __init__(self, name, host, db):
        super().__init__(name, 'MongoDB', host)
        self.db = db

    def check_status(self):
        try:
            client = MongoClient(self.host)
            client.admin.command('ismaster')
            return "Online"
        except ConnectionFailure:
            return "Offline"

class WebAppService(Service):
    def __init__(self, name, host, healthcheck, response_type):
        super().__init__(name, 'WebApp', host)
        self.healthcheck = healthcheck
        self.response_type = response_type

    def check_status(self):
        try:
            url = f"{self.host}{self.healthcheck}"
            response = requests.get(url)
            if self.response_type == "JSON":
                response.json()
            elif self.response_type == "TEXT":
                response.text
            return "Online" if response.status_code == 200 else "Offline"
        except Exception as e:
            return f"Offline: {e}"

# Factory method to create services
def create_service(service_data):
    if service_data['Type'] == 'MongoDB':
        return MongoDBService(service_data['Name'], service_data['Host'], service_data['DB'])
    elif service_data['Type'] == 'WebApp':
        return WebAppService(service_data['Name'], service_data['Host'], service_data['Healthcheck'], service_data['Response'])
    else:
        raise ValueError("Unsupported service type")
