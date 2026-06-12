import requests
import configparser
from core.utils import Utils
import json


class JenkinsRequestError(Exception):
    """Request failure carrying a short, user-readable message."""


def _friendly_error(e):
    # Order matters: SSLError and ConnectTimeout are subclasses of
    # ConnectionError/Timeout, so check the specific ones first.
    if isinstance(e, requests.exceptions.SSLError):
        return "SSL error while connecting to the server."
    if isinstance(e, (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError)):
        return "Server unreachable. Check the server URL and your network connection."
    if isinstance(e, requests.exceptions.Timeout):
        return "The server took too long to respond."
    if isinstance(e, (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL)):
        return "Invalid server URL. Check the settings."
    return str(e)


class JenkinsRequestor:

    TIMEOUT = (5, 15)  # (connect, read): fail fast when unreachable, allow time for Groovy
    HEALTHCHECK_TIMEOUT = 5  # short timeout for the status dot, so it reacts fast

    def __init__(self, config: configparser):
        self.config = config
        self.session = requests.Session()
        self.update_auth()

    def update_auth(self):
        path = Utils.get_config_path("jenkins-decryptor")
        self.config.read(path)
        has = self.config.has_section('settings')
        self.username = self.config['settings'].get('username', '') if has else ""
        self.server_url = self.config['settings'].get('server_url', '') if has else ""
        self.token = Utils.get_token(self.username, self.config)
    
    def post(self, script):
        self.update_auth()
        try:
            return self.session.post(
                self.server_url+"/scriptText",
                auth=(self.username, self.token),
                data={"script": script},
                timeout=self.TIMEOUT
            )
        except requests.RequestException as e:
            raise JenkinsRequestError(_friendly_error(e)) from e

    def test_auth(self):
        # Lightweight read-only health check on /me/api/json: no Groovy execution
        # (so it doesn't need the Script Console permission just for the status
        # dot, nor spam the audit log), short timeout. /me/ requires an
        # authenticated user, so a wrong token gives 401 (red dot) even when
        # anonymous read access is enabled.
        self.update_auth()
        if not self.server_url:
            return False
        try:
            response = self.session.get(
                self.server_url + "/me/api/json",
                auth=(self.username, self.token),
                timeout=self.HEALTHCHECK_TIMEOUT
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def test(self, server, user, tkn):
        try:
            response = self.session.post(
                server +"/scriptText",
                auth=(user, tkn),
                data={"script": "print \"testok\""},
                timeout=self.TIMEOUT
            )
            if response.status_code == 200:
                if response.text == "testok":
                    return True
        except:
            return False
    
    def _build_credential_payload(self, credential_type, **kwargs):
        # "stapler-class" is the current key Jenkins uses to resolve the
        # implementation class when binding the JSON; "$class" is the legacy
        # one. Send both so create and update work across plugin versions.
        if credential_type == "SecretText":
            return {
                "scope": "GLOBAL",
                "id": kwargs.get("credential_id", ""),
                "secret": kwargs.get("secret", ""),
                "description": kwargs.get("credential_id", ""),
                "stapler-class": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl",
                "$class": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl"
            }
        if credential_type == "UsernamePassword":
            return {
                "scope": "GLOBAL",
                "id": kwargs.get("credential_id", ""),
                "username": kwargs.get("username", ""),
                "password": kwargs.get("password", ""),
                "description": kwargs.get("credential_id", ""),
                "stapler-class": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl",
                "$class": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl"
            }
        return None

    def _post_credential_form(self, url, payload, success_msg):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            data = {'json': json.dumps(payload)}
            response = self.session.post(url, auth=(self.username, self.token), headers=headers, data=data, timeout=self.TIMEOUT)
            if response.status_code == 200:
                return True, success_msg
            else:
                return False, f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return False, _friendly_error(e)

    def post_create_credential(self, credential_type, **kwargs):
        self.update_auth()
        credentials = self._build_credential_payload(credential_type, **kwargs)
        if credentials is None:
            return False, f"Type '{credential_type}' not supported."
        url = f"{self.server_url}/credentials/store/system/domain/_/createCredentials"
        return self._post_credential_form(url, {"": "0", "credentials": credentials}, "Credential created successfully.")

    def update_credential(self, credential_type, **kwargs):
        # Atomic update via the credential's updateSubmit endpoint (the same
        # call the Jenkins web UI makes). Unlike delete-then-recreate, the old
        # credential survives if the request fails or the connection drops.
        self.update_auth()
        credential_id = kwargs.get("credential_id", "")
        if not credential_id:
            return False, "Missing credential ID."
        credentials = self._build_credential_payload(credential_type, **kwargs)
        if credentials is None:
            return False, f"Type '{credential_type}' not supported."
        url = f"{self.server_url}/credentials/store/system/domain/_/credential/{credential_id}/updateSubmit"
        return self._post_credential_form(url, credentials, "Credential updated successfully.")
    
    def delete_credential(self, credential_id):
        url = f"{self.server_url}/credentials/store/system/domain/_/credential/{credential_id}/doDelete"
        try:
            response = self.session.post(url, auth=(self.username, self.token), timeout=self.TIMEOUT)
            if response.status_code == 200:
                return True, "Credential deleted."
            else:
                return False, f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return False, _friendly_error(e)

