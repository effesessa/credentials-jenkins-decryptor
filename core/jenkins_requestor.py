import requests
import configparser
from core.utils import Utils
from functools import singledispatch

class JenkinsRequestor:

    def __init__(self, config: configparser):
        self.config = config
        self.update_auth()
    
    def update_auth(self):
        path = Utils.get_config_path("jenkins-decryptor")
        self.config.read(path)
        self.username = self.config['settings'].get('username', '') if self.config.has_section('settings') else ""
        self.token = self.config['settings'].get('token', '') if self.config.has_section('settings') else ""
        self.server_url = self.config['settings'].get('server_url', '') if self.config.has_section('settings') else ""
    
    def post(self, script):
        self.update_auth()
        return requests.post(
            self.server_url+"/scriptText",
            auth=(self.username, self.token),
            data={"script": script}
        )

    def test_auth(self):
        self.update_auth()
        try:
            response = requests.post(
                self.server_url +"/scriptText",
                auth=(self.username, self.token),
                data={"script": "print \"testok\""}
            )
            if response.status_code == 200:
                if response.text == "testok":
                    return True
        except:
            return False
    
    def test(self, server, user, tkn):
        try:
            response = requests.post(
                server +"/scriptText",
                auth=(user, tkn),
                data={"script": "print \"testok\""}
            )
            if response.status_code == 200:
                if response.text == "testok":
                    return True
        except:
            return False