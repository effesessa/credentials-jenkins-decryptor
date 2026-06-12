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
  - Configure your Jenkins server URL, username and API token. Server URL, username, theme and language are saved to a local `.ini` file:
    - On **Windows**: `C:\Users\<YourUsername>\AppData\Roaming\jenkins-decryptor\config.ini`
    - On **macOS/Linux**: `~/.config/jenkins-decryptor/config.ini`
- **Secure token storage**:
  - The API token is stored in the **OS keyring** (Windows Credential Manager / macOS Keychain / Linux Secret Service), not in plaintext. If no keyring backend is available, it falls back to the `.ini` file.
- **Connection status**:
  - A status dot shows at a glance whether the configured server is reachable and the credentials authenticate.
- **Theme Options**:
  - Choose between **Light** and **Dark** themes (default: Dark).
- **Language**:
  - Switch the interface between **English** and **Italian** from Settings — applied instantly.
- **Check for Updates**:
  - From **Help → Check for Updates**, the app checks the latest GitHub release and offers to open the download page when a newer version is available.

---

## 🛠️ Technical Details

- **Jenkins Version Tested**: `2.440.1`
- **Python Version Used**: `3.13.0`
- **Requirements**: the Jenkins **Script Console** must be enabled and the authenticated user must have the **Groovy Script Console** permission (used to search and read credential values).

---

## ▶️ How to Use (Download & Run)

The quickest way to use the app — no Python, no build required.

### 1. Download the latest release
Go to the [**Releases**](https://github.com/effesessa/credentials-jenkins-decryptor/releases/latest) page and download the Windows ZIP asset (e.g. `credentials-jenkins-decryptor-vX.Y-windows.zip`).

### 2. Extract and run
Unzip the archive anywhere and open the extracted folder, then double-click **`CredentialsJenkinsDecryptor.exe`**. No installation needed.

> Keep the `.exe` together with the `_internal` folder — the app needs both, so don't move the `.exe` out on its own. 
To launch it conveniently from anywhere (Desktop, Start menu, taskbar), **create a shortcut** instead.

### 3. Configure your Jenkins connection
On first launch, open **File → Settings** and fill in:
- **Server address** — e.g. `https://jenkins.company.com`
- **Username** — your Jenkins user
- **API token** — generate one in Jenkins under *Your profile → Security → API Token*

Click **Test connection** to verify, then **Save**. The status dot in the corner turns green when the server is reachable and your credentials authenticate.

> **Prerequisite:** the Jenkins **Script Console** must be enabled and your user must have the **Groovy Script Console** permission — this is what the app uses to search and decrypt credential values.

### 4. Find and read a credential
- Type part of a credential **ID** in the search box and press Enter.
- Click a result to view it. Secret/password fields are masked — use the 👁 toggle to reveal, and 📋 to copy.
- For **File** credentials, right-click the content to download it.

### 5. Manage credentials
From the result view you can **edit/update** or **delete** a credential, and from **File → Create Credential** you can add a new `UsernamePassword` or `Secret Text` credential.

### Optional
- **Language:** switch between English and Italian in Settings.
- **Theme:** toggle Light/Dark in Settings.
- **Updates:** check for a newer version any time via **Help → Check for Updates**.

---

## 📦 Installation and Build App

> This section is for developers who want to run from source or build the executable themselves. End users should follow the **How to Use (Download & Run)** section above.

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
pyinstaller --onedir --windowed --name "CredentialsJenkinsDecryptor" \
--icon="./images/jenkinsd-transformed.ico" \
--add-data "images/jenkinsd-transformed.webp:./images" \
--add-data "images/jenkinsd-transformed.ico:./images" \
--add-data "images/key-4.png:./images" \
--add-data "groovy/find_contains.groovy:./groovy" \
--add-data "groovy/get_value.groovy:./groovy" \
app.py
```
> On **Windows**, the `--add-data` separator must be `;` instead of `:`. PyInstaller does not cross-compile: build on Windows for the Windows release, on Linux for a Linux build.

After running this command, a new `dist/CredentialsJenkinsDecryptor/` directory is created containing the generated executable and its `_internal` folder.

### 5. Run the application
Open `dist/CredentialsJenkinsDecryptor/` and run **`CredentialsJenkinsDecryptor.exe`**.
