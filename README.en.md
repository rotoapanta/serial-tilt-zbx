[![Python](https://img.shields.io/badge/Python-3.11-brightgreen)](https://www.python.org/) 
![GitHub issues](https://img.shields.io/github/issues/rotoapanta/raspberry-api) 
![GitHub repo size](https://img.shields.io/github/repo-size/rotoapanta/raspberry-api) 
![GitHub last commit](https://img.shields.io/github/last-commit/rotoapanta/raspberry-api)
[![Discord Invite](https://img.shields.io/badge/discord-join%20now-green)](https://discord.gg/bf6rWDbJ) 
[![Docker](https://img.shields.io/badge/Docker-No-brightgreen)](https://www.docker.com/) 
[![GitHub](https://img.shields.io/badge/GitHub-Project-brightgreen)](https://github.com/rotoapanta/raspberry-api) 
[![Linux](https://img.shields.io/badge/Linux-Supported-brightgreen)](https://www.linux.org/) 
[![Author](https://img.shields.io/badge/Roberto%20-Toapanta-brightgreen)](https://www.linkedin.com/in/roberto-carlos-toapanta-g/) 
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)](#change-log) 
![GitHub forks](https://img.shields.io/github/forks/rotoapanta/raspberry-api?style=social) 
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# <p align="center">Serial-Tilt-ZBX</p>

This project reads, processes, and sends data from inclinometers and pluviometers via serial ports to a Zabbix server for real-time monitoring.

## Features

- **Concurrent Reading:** Monitors multiple serial ports simultaneously.
- **Data Processing:** Parses specific data frames from the sensors.
- **Zabbix Integration:** Uses `zabbix_sender` to send metrics to a Zabbix server.
- **Robust Logging:** Logs application activity, including errors, with file rotation.
- **Flexible Configuration:** Manages port and Zabbix settings through external files.
- **Automated Setup:** Includes scripts to facilitate setup on a Raspberry Pi.
- **Service Execution:** Allows installation as a `systemd` service for continuous operation.

## System Requirements

This project is designed for Debian-based operating systems (like Raspberry Pi OS, Ubuntu, etc.). Before installation, ensure your system has the following packages. The `setup_pi.sh` script will attempt to install them automatically.

- `python3`
- `python3-venv` (for creating virtual environments)
- `git` (for cloning the repository)
- `zabbix-sender` (for sending data to Zabbix)

---

## Raspberry Pi Deployment (Recommended)

This is the recommended way to deploy the system in a production environment. The scripts automate dependency installation and service setup.

### 1. Preparation

- Clone this repository to your Raspberry Pi:
  ```bash
  git clone https://github.com/your-user/serial-tilt-zbx.git
  cd serial-tilt-zbx
  ```

### 2. Run the Setup Script

- This script will install system dependencies (like `python3-venv` and `zabbix-sender`) and the necessary Python libraries.
  ```bash
  chmod +x setup_pi.sh
  ./setup_pi.sh
  ```
  *Note: The script may ask for your `sudo` password if it needs to install system packages.*

### 3. Configure the Application

- **VERY IMPORTANT!** Edit the configuration files to match your hardware and server.
  - `config/serial_config.py`: Adjust the serial port names (e.g., `/dev/ttyUSB0`).
  - `config/zabbix_config.py`: Set your Zabbix server address.
  - `config/station_mapping.py`: Map station IDs to Zabbix host names.

### 4. Install as a Service (Optional but Recommended)

- To have the application start automatically and keep running, install it as a `systemd` service.
  ```bash
  chmod +x install_service.sh
  ./install_service.sh
  ```
- The script will generate a `.service` file and show you the exact commands to move, enable, and start it. Follow the instructions in the terminal.

- **To manage the service:**
  - **Check status:** `sudo systemctl status serial-tilt-zbx.service`
  - **View logs:** `journalctl -u serial-tilt-zbx.service -f`

---

## Manual Installation (Development Environment)

Follow these steps for a manual installation on any Linux system.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-user/serial-tilt-zbx.git
   cd serial-tilt-zbx
   ```

2. **Install `zabbix-sender`:**
   - On Debian/Ubuntu/Raspberry Pi OS systems:
     ```bash
     sudo apt-get update && sudo apt-get install zabbix-sender
     ```

3. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure and run:**
   - Edit the files in the `config/` directory.
   - Run the application:
     ```bash
     python main.py
     ```

## Testing

To run the unit tests, use the following command from the project's root directory:

```bash
python -m unittest discover tests
```
