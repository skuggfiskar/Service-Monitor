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
    def __init__(self, name, host, healthcheck, response):
        super().__init__(name, 'WebApp', host)
        self.healthcheck = healthcheck
        self.response = response

    def check_status(self):
        try:
            url = f"{self.host}{self.healthcheck}"
            response = requests.get(url)
            if self.response['ExpectedStatusCode'] != None and response.status_code != self.response['ExpectedStatusCode']: # todo allow any
                return f"Offline: Expected {self.response['ExpectedStatusCode']}, got {response.status_code}"
            if self.response['Type'] == "JSON":
                expected_content = self.response.get('ExpectedContent')
                if expected_content and response.json() != expected_content:
                    return "Offline: Unexpected JSON response"
            elif self.response['Type'] == "TEXT":
                expected_content = self.response.get('ExpectedContent')
                if expected_content and response.text != expected_content:
                    return "Offline: Unexpected text response"
            return "Online"
        except Exception as e:
            return f"Offline: {e}"

def create_service(service_data):
    if service_data['Type'] == 'MongoDB':
        return MongoDBService(service_data['Name'], service_data['Host'], service_data['DB'])
    elif service_data['Type'] == 'WebApp':
        return WebAppService(service_data['Name'], service_data['Host'], service_data['Healthcheck'], service_data['Response'])
    else:
        raise ValueError("Unsupported service type")
