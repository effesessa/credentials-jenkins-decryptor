import requests
import configparser
from core.utils import Utils
import json

class JenkinsRequestor:

    TIMEOUT = 30
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
        return self.session.post(
            self.server_url+"/scriptText",
            auth=(self.username, self.token),
            data={"script": script},
            timeout=self.TIMEOUT
        )

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
    
    def post_create_credential(self, credential_type, **kwargs):
        url = f"{self.server_url}/credentials/store/system/domain/_/createCredentials"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        if credential_type == "SecretText":
            payload = {
                "": "0",
                "credentials": {
                    "scope": "GLOBAL",
                    "id": kwargs.get("credential_id", ""),
                    "secret": kwargs.get("secret", ""),
                    "description": kwargs.get("credential_id", ""),
                    "$class": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl"
                }
            }
        elif credential_type == "UsernamePassword":
            payload = {
                "": "0",
                "credentials": {
                    "scope": "GLOBAL",
                    "id": kwargs.get("credential_id", ""),
                    "username": kwargs.get("username", ""),
                    "password": kwargs.get("password", ""),
                    "description": kwargs.get("credential_id", ""),
                    "$class": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl"
                }
            }
        else:
            return False, f"Type '{credential_type}' not supported."

       
        
        try:
            data = {'json': json.dumps(payload)}
            response = self.session.post(url, auth=(self.username, self.token), headers=headers, data=data, timeout=self.TIMEOUT)
            if response.status_code == 200:
                return True, "Credenziale creata con successo."
            else:
                return False, f"Errore {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Eccezione durante la richiesta: {e}"

    def update_credential(self, credential_type, **kwargs):
        self.update_auth()
        credential_id = kwargs.get("credential_id", "")
        if not credential_id:
            return False, "ID della credenziale mancante."

        # 1. Elimina la credenziale esistente
        delete_success, delete_msg = self.delete_credential(credential_id)
        if not delete_success:
            return False, f"Errore durante l'eliminazione: {delete_msg}"

        # 2. Ricrea la credenziale aggiornata
        return self.post_create_credential(credential_type, **kwargs)
    
    def delete_credential(self, credential_id):
        url = f"{self.server_url}/credentials/store/system/domain/_/credential/{credential_id}/doDelete"
        try:
            response = self.session.post(url, auth=(self.username, self.token), timeout=self.TIMEOUT)
            if response.status_code == 200:
                return True, "Credenziale eliminata."
            else:
                return False, f"Errore {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Eccezione durante la richiesta: {e}"

