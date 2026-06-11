# Credentials Jenkins Decryptor

<img src="images/jenkinsd-transformed.webp" width="200"/>

Effortlessly retrieve decrypted credentials from Jenkins in just a few clicks! This tool simplifies the process of extracting plaintext credentials stored on a Jenkins server, eliminating the tedious and time-consuming steps described in various online guides.

---

## 🌟 Why This Project?

Managing credentials on Jenkins servers can be cumbersome. To retrieve plaintext values of stored credentials, you often need to follow a series of complex steps that take several minutes. This project was born to streamline and automate that process, making it faster and more user-friendly.

---

## 🚀 Features

- **Supported Credential Types**:
  - `UsernamePassword`
  - `File`
  - `String` or `Secret`
- **Search Functionality**:
  - Quickly find credentials by searching with keywords or text contained in a credential ID (supports `contains` search).
- **Credential Actions**:
  - **View & copy** `UsernamePassword` and `String/Secret` credentials with a single click. Secret/password fields are **masked by default**, with a reveal (👁) toggle.
  - **Create** new credentials (`UsernamePassword`, `Secret Text`).
  - **Edit/update** existing credentials in place.
  - **Delete** credentials (with a confirmation step).
  - **Download** `File` credentials by right-clicking and choosing where to save.
- **Server Configuration**:
  - Configure your Jenkins server URL, username and API token. Server URL, username and theme are saved to a local `.ini` file:
    - On **Windows**: `C:\Users\<YourUsername>\AppData\Roaming\jenkins-decryptor\config.ini`
    - On **macOS/Linux**: `~/.config/jenkins-decryptor/config.ini`
- **Secure token storage**:
  - The API token is stored in the **OS keyring** (Windows Credential Manager / macOS Keychain / Linux Secret Service), not in plaintext. If no keyring backend is available, it falls back to the `.ini` file.
- **Connection status**:
  - A status dot shows at a glance whether the configured server is reachable and the credentials authenticate.
- **Theme Options**:
  - Choose between **Light** and **Dark** themes (default: Dark).

---

## 🛠️ Technical Details

- **Jenkins Version Tested**: `2.440.1`
- **Python Version Used**: `3.13.0`
- **Requirements**: the Jenkins **Script Console** must be enabled and the authenticated user must have the **Groovy Script Console** permission (used to search and read credential values).

---

## 📦 Installation and Build App

Follow these steps to install and build the application executable.

### 1. Clone the repository
Clone the GitHub repository to your local system:
```bash
git clone https://github.com/effesessa/credentials-jenkins-decryptor.git
cd credentials-jenkins-decryptor
```

### 2. Install dependencies
Install the required Python libraries listed in the requirements.txt:
```bash
pip install -r requirements.txt
```

### 3. Install PyInstaller
Install PyInstaller to build the application executable:
```bash
pip install pyinstaller
```

### 4. Build the application
Run the following command to build the application executable:
```bash
pyinstaller --onedir --windowed \
--icon="./images/jenkinsd-transformed.ico" \
--add-data "images/jenkinsd-transformed.webp:./images" \
--add-data "images/jenkinsd-transformed.ico:./images" \
--add-data "images/key-4.png:./images" \
--add-data "groovy/find_contains.groovy:./groovy" \
--add-data "groovy/get_value.groovy:./groovy" \
app.py
```
After running this command, a new directory called dist will be created in your project folder. Inside the dist directory, you'll find the folder containing the generated executable.

### 5. Run the application
Navigate to the dist directory and locate the generated application folder. Run the executable file.

---
</br>
<img src="images/home.jpg" width="800"/></br></br>

<img src="images/settings.jpg" width="800"/></br>

<img src="images/userpsw.jpg" width="800"/></br>
