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
- **Server Configuration**:
  - Easily set up your Jenkins server, username, and API token (created in Jenkins).
- **Search Functionality**:
  - Quickly find credentials by searching with keywords or text contained in a credential (supports `contains` search).
- **Credential Actions**:
  - View and copy `UsernamePassword` and `String/Secret` credentials with a single click.
  - Download `File` credentials by right-clicking and selecting the desired save location.
- **Theme Options**:
  - Choose between **Light** and **Dark** themes (default: Dark).

---

## 🛠️ Technical Details

- **Jenkins Version Tested**: `2.440.1`
- **Python Version Used**: `3.13.0`

---

## 📦 Installation

To install and create an executable for the app, the project uses **PyInstaller**. Follow these steps:

