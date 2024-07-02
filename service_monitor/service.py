import threading
import subprocess
import time
import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import redis
import os
import signal

class Service:
    def __init__(self, name, service_type, host, interval=10, command=None, command_type=None):
        self.name = name
        self.service_type = service_type
        self.host = host
        self.interval = interval
        self.command = command
        self.command_type = command_type
        self.status = "Unknown"
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._process = None  # Variable to store the process object

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._process:
            self.stop_command()

    def _run(self):
        while not self._stop_event.is_set():
            self.status = self.check_status()
            time.sleep(self.interval)
    
    def run_command(self):
        if self.command:
            if self.command_type == "run":
                def target():
                    self._process = subprocess.Popen(self.command, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, shell=True)
                threading.Thread(target=target, daemon=True).start()
            elif self.command_type == "start":
                self._process = subprocess.call(self.command, shell=True)
            else:
                raise ValueError("Unsupported command type")
    
    def stop_command(self):
        if self.command_type == "run":
            if self._process and self._process.poll() is None:  # Check if the process is still running
                print("Killing process...")
                self._process.send_signal(signal.CTRL_BREAK_EVENT)
                self._process.kill()
        elif self.command_type == "start":
            raise ValueError("Cannot stop a command that was started")
        else:
            raise ValueError("Unsupported command type")

    def check_status(self):
        raise NotImplementedError("Must be implemented by subclasses")

class MongoDBService(Service):
    def __init__(self, name, host, db, interval=10, command=None, command_type=None):
        super().__init__(name, 'MongoDB', host, interval, command, command_type)
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
    def __init__(self, name, host, healthcheck, response, interval=10, command=None, command_type=None):
        super().__init__(name, 'WebApp', host, interval, command, command_type)
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

class RedisService(Service):
    def __init__(self, name, host, port, interval=10, command=None, command_type=None):
        super().__init__(name, 'Redis', host, interval, command, command_type)
        self.port = port
        self.start()  # Start the service thread

    def check_status(self):
        try:
            client = redis.Redis(host=self.host, port=self.port)
            if client.ping():
                return "Online"
            else:
                return "Offline"
        except redis.ConnectionError:
            return "Offline"

def create_service(service_data):
    interval = service_data.get('Interval', 10)  # Default interval is 10 seconds
    command = service_data.get('Command', None)
    command_type = service_data.get('CommandType', None)
    if service_data['Type'] == 'MongoDB':
        return MongoDBService(service_data['Name'], service_data['Host'], service_data['DB'], interval, command, command_type)
    elif service_data['Type'] == 'WebApp':
        return WebAppService(service_data['Name'], service_data['Host'], service_data['Healthcheck'], service_data['Response'], interval, command, command_type)
    elif service_data['Type'] == 'Redis':
        return RedisService(service_data['Name'], service_data['Host'], service_data['Port'], interval, command, command_type)
    else:
        raise ValueError("Unsupported service type")
