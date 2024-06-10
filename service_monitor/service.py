import threading
import time
import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class Service:
    def __init__(self, name, service_type, host, interval=10):
        self.name = name
        self.service_type = service_type
        self.host = host
        self.interval = interval
        self.status = "Unknown"
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _run(self):
        while not self._stop_event.is_set():
            self.status = self.check_status()
            time.sleep(self.interval)

    def check_status(self):
        raise NotImplementedError("Must be implemented by subclasses")

class MongoDBService(Service):
    def __init__(self, name, host, db, interval=10):
        super().__init__(name, 'MongoDB', host, interval)
        self.db = db
        self.start()  # Start the service thread

    def check_status(self):
        try:
            client = MongoClient(self.host)
            client.admin.command('ismaster')
            return "Online"
        except ConnectionFailure:
            return "Offline"

class WebAppService(Service):
    def __init__(self, name, host, healthcheck, response, interval=10):
        super().__init__(name, 'WebApp', host, interval)
        self.healthcheck = healthcheck
        self.response = response
        self.start()  # Start the service thread

    def check_status(self):
        try:
            url = f"{self.host}{self.healthcheck}"
            response = requests.get(url)
            if self.response['ExpectedStatusCode'] is not None and response.status_code != self.response['ExpectedStatusCode']:
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
    interval = service_data.get('Interval', 10)  # Default interval is 10 seconds
    if service_data['Type'] == 'MongoDB':
        return MongoDBService(service_data['Name'], service_data['Host'], service_data['DB'], interval)
    elif service_data['Type'] == 'WebApp':
        return WebAppService(service_data['Name'], service_data['Host'], service_data['Healthcheck'], service_data['Response'], interval)
    else:
        raise ValueError("Unsupported service type")
