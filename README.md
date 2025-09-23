[![Python](https://img.shields.io/badge/Python-3.11-brightgreen)](https://www.python.org/) 
![GitHub issues](https://img.shields.io/github/issues/rotoapanta/serial-tilt-zbx) 
![GitHub repo size](https://img.shields.io/github/repo-size/rotoapanta/serial-tilt-zbx) 
![GitHub last commit](https://img.shields.io/github/last-commit/rotoapanta/serial-tilt-zbx)
[![Discord Invite](https://img.shields.io/badge/discord-join%20now-green)](https://discord.gg/bf6rWDbJ) 
[![Docker](https://img.shields.io/badge/Docker-No-brightgreen)](https://www.docker.com/) 
[![Linux](https://img.shields.io/badge/Linux-Supported-brightgreen)](https://www.linux.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Author](https://img.shields.io/badge/Roberto%20-Toapanta-brightgreen)](https://www.linkedin.com/in/roberto-carlos-toapanta-g/) 
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)](#change-log) 
![GitHub forks](https://img.shields.io/github/forks/rotoapanta/serial-tilt-zbx?style=social) 

# <p align="center">Serial Tiltmeter to Zabbix</p>

This project reads, processes, and sends data from inclinometers and pluviometers via serial ports to a Zabbix server for real-time monitoring.

## Features

- Concurrent Reading: Monitors multiple serial ports simultaneously.
- Data Processing: Parses specific data frames from the sensors.
- Zabbix Integration: Uses `zabbix_sender` to send metrics to a Zabbix server.
- Robust Logging: Logs application activity, including errors, with file rotation.
- Graceful Shutdown: Handles SIGINT/SIGTERM to stop threads cleanly.
- Thread-Safe Storage: Prevents race conditions when writing TSV files.
- Flexible Configuration: Manages port and Zabbix settings through external files.
- Automated Setup: Includes scripts to facilitate setup on a Raspberry Pi.
- Service Execution: Allows installation as a `systemd` service for continuous operation.
- Serial Port Resilience: Configurable retry policy per port and an auto re-enable supervisor when ports recover.

## System Requirements

This project is designed for Debian-based operating systems (like Raspberry Pi OS, Ubuntu, etc.). Before installation, ensure your system has the following packages. The `setup_pi.sh` script will attempt to install them automatically.

- python3
- python3-venv (for creating virtual environments)
- git (for cloning the repository)
- zabbix-sender (for sending data to Zabbix)

## Project Structure

```
serial-tilt-zbx/
├── config/
│   ├── app_config.py
│   ├── serial_config.py
│   ├── station_mapping.py
│   └── zabbix_config.py
├── parsers/
│   └── data_parser.py
├── tests/
│   └── test_data_parser.py
├── utils/
│   ├── data_processor.py
│   ├── data_storage.py
│   ├── logging_config.py
│   ├── serial_reader.py
│   └── zabbix_sender.py
├── .gitignore
├── config.json
├── install_service.sh
├── main.py
├── README.es.md
├── README.md
├── requirements.txt
└── setup_pi.sh
```

---

## Raspberry Pi Deployment (Recommended)

This is the recommended way to deploy the system in a production environment. The scripts automate dependency installation and service setup.

### 1. Preparation

- Clone this repository to your Raspberry Pi:
  ```bash
  git clone https://github.com/rotoapanta/serial-tilt-zbx.git
  cd serial-tilt-zbx
  ```

### 2. Run the Setup Script

- This script will install system dependencies (like `python3-venv` and `zabbix-sender`) and the necessary Python libraries. It runs apt non-interactively and upgrades pip/setuptools/wheel before installing requirements.
  ```bash
  chmod +x setup_pi.sh
  ./setup_pi.sh
  ```
  Note: The script may ask for your `sudo` password if it needs to install system packages.

### 3. Configure the Application

- VERY IMPORTANT: Edit the configuration files to match your hardware and server.
  - `config.json`: Define `serial_ports` and (optionally) retry/supervisor settings under `serial_retry` and `serial_supervisor`.
  - `config/zabbix_config.py`: Set your Zabbix server address.
  - `config/station_mapping.py`: Map station IDs to Zabbix host names.

### Optional: Serial permissions and stable device names

- Add your user to the `dialout` group, then log out/in:
  ```bash
  sudo usermod -a -G dialout $USER
  # Log out and back in to apply
  ```
- Create udev rules for stable names:
  ```bash
  sudo tee /etc/udev/rules.d/99-serial-names.rules >/dev/null <<'R'
  SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", SYMLINK+="ttyUSB_TILT"
  SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="ttyUSB_PLUV"
  R
  sudo udevadm control --reload-rules && sudo udevadm trigger
  ```
  Then reference `/dev/ttyUSB_TILT`, `/dev/ttyUSB_PLUV` in your config.

### 4. Install as a Service (Optional but Recommended)

- To have the application start automatically and keep running, install it as a `systemd` service.
  ```bash
  chmod +x install_service.sh
  ./install_service.sh
  ```
- The script will generate a `.service` file and show you the exact commands to move, enable, and start it. Follow the instructions in the terminal. The generated unit uses Type=simple, Restart=on-failure, LimitNOFILE=4096, and supports an optional EnvironmentFile at `/etc/default/serial-tilt-zbx`.

  Or run the following commands explicitly:
  ```bash
  sudo mv $(pwd)/serial-tilt-zbx.service /etc/systemd/system/serial-tilt-zbx.service
  sudo systemctl daemon-reload
  sudo systemctl enable serial-tilt-zbx.service
  sudo systemctl start serial-tilt-zbx.service
  ```

- To manage the service:
  - Check status: `sudo systemctl status serial-tilt-zbx.service`
  - View logs: `journalctl -u serial-tilt-zbx.service -f`

---

## Manual Installation (Development Environment)

Follow these steps for a manual installation on any Linux system.

1. Clone the repository:
   ```bash
   git clone https://github.com/rotoapanta/serial-tilt-zbx.git
   cd serial-tilt-zbx
   ```

2. Install `zabbix-sender`:
   - On Debian/Ubuntu/Raspberry Pi OS systems:
     ```bash
     sudo apt-get update && sudo apt-get install zabbix-sender
     ```

3. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install Python dependencies:
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

5. Configure and run:
   - Edit the files in the `config/` directory.
   - Run the application:
     ```bash
     python main.py
     ```

## Serial retry and supervisor configuration

- Global defaults in `config.json`:
  - `serial_retry`: `{ "max_attempts": 3, "delay_seconds": 5, "on_fail": "disable" }`
  - `serial_supervisor`: `{ "auto_reenable": true, "reenable_interval_seconds": 20 }`
- Per-port overrides: add `max_retries`, `retry_delay`, `on_fail` inside a specific `serial_ports` entry.
- Behavior:
  - After `max_attempts` failures: `on_fail` determines whether to keep retrying, disable the port thread, or stop the app.
  - Disabled ports are probed by the supervisor and re-enabled automatically when available.

Example snippet from `config.json`:

```json
{
  "serial_ports": [
    { "port": "/dev/ttyUSB0", "baudrate": 9600, "bytesize": 8, "parity": "N", "stopbits": 1, "timeout": 1 },
    { "port": "/dev/ttyUSB4", "baudrate": 9600, "bytesize": 8, "parity": "N", "stopbits": 1, "timeout": 1,
      "max_retries": 3, "retry_delay": 5, "on_fail": "disable" }
  ],
  "serial_retry": { "max_attempts": 3, "delay_seconds": 5, "on_fail": "disable" },
  "serial_supervisor": { "auto_reenable": true, "reenable_interval_seconds": 20 }
}
```

Notes:
- Changes to `config.json` apply after restarting the application.
- Logs will show when a port is disabled and when it is re-enabled by the supervisor.

## Testing

To run the unit tests, use the following command from the project's root directory:

```bash
python -m unittest discover tests
```

## Console output example

```
(venv) pi@raspi-tilt:~/Documents/Projects/serial-tilt-zbx $ python main.py
2025-09-22 16:47:08,333 - root - INFO - ==================================================
2025-09-22 16:47:08,334 - root - INFO - Serial Tiltmeter to Zabbix Application Started
2025-09-22 16:47:08,335 - root - INFO - ==================================================
2025-09-22 16:47:08,336 - utils.zabbix_sender - INFO - zabbix_sender binary found.
2025-09-22 16:47:08,349 - utils.zabbix_sender - INFO - Connectivity to Zabbix 192.168.XXX.YYY:10051 OK.
2025-09-22 16:47:08,350 - root - INFO - Starting serial port readers...
2025-09-22 16:47:08,361 - utils.serial_reader - INFO - Successfully opened port /dev/ttyUSB0
2025-09-22 16:47:08,363 - utils.serial_reader - INFO - Successfully opened port /dev/ttyUSB2
2025-09-22 16:47:08,364 - utils.serial_reader - INFO - Successfully opened port /dev/ttyUSB1
2025-09-22 16:47:08,367 - utils.serial_reader - INFO - Successfully opened port /dev/ttyUSB3
2025-09-22 16:47:08,368 - utils.serial_reader - INFO - Successfully opened port /dev/ttyUSB4
2025-09-22 16:47:27,921 - utils.data_processor - INFO - 2025-09-22 16:47:27 - /dev/ttyUSB3: {'type': 'TILT_RAIN', 'station_name': 'GGPA', 'station_type': 1, 'station_number': 11, 'network_id': 1, 'inclinometer': {'radial': -427.5, 'tangential': 296.3, 'temperature': 6.1, 'voltage': 13.7}, 'pluviometer': {'rain_level': 0.0, 'voltage': 13.7}}
2025-09-22 16:47:27,962 - utils.zabbix_sender - INFO - Sent 4 metrics to Zabbix 192.168.1.143:10051 for host GGPA_IN.
2025-09-22 16:47:27,997 - utils.zabbix_sender - INFO - Sent 2 metrics to Zabbix 192.168.1.143:10051 for host GGPA_PL.
```

## Feedback

If you have any feedback, please reach out to us at robertocarlos.toapanta@gmail.com

## Support

For support, email robertocarlos.toapanta@gmail.com or join our Discord channel.

## License

[MIT](https://opensource.org/licenses/MIT)

## Authors

- [@rotoapanta](https://github.com/rotoapanta)

## Change log

[Unreleased]
- Added
  - Project Structure section placed after "System Requirements".
- Changed
  - License updated to MIT.
  - README.es.md synchronized with README.md.
  - Minor structure/wording adjustments in README files.
- Fixed
  - Removed a minor encoding artifact in README.

1.0.0 – 2025-09-22
- Added
  - Initial release: concurrent serial reading, sensor frame parsing (inclinometer and pluviometer), Zabbix sender integration, robust logging with rotation, graceful shutdown, thread-safe TSV storage, externalized configuration, Raspberry Pi setup scripts, optional systemd service, serial retry/supervisor, and basic unit tests for the parser.

## More Info

- Zabbix sender utility: https://www.zabbix.com/documentation/current/en/manual/concepts/sender
- Zabbix trapper items: https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/trapper
- PySerial (serial communication): https://pyserial.readthedocs.io/en/latest/pyserial.html
- systemd services: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
- udev rules (persistent device names): https://wiki.archlinux.org/title/Udev
- Python logging cookbook: https://docs.python.org/3/howto/logging-cookbook.html
- Python virtual environments (venv): https://docs.python.org/3/library/venv.html
- unittest framework: https://docs.python.org/3/library/unittest.html

## Zabbix templates and host linking

- Import the templates from the templates/ directory:
  - templates/zbx_export_templates_inclinometro.yaml
  - templates/zbx_export_templates_pluviometro.yaml
- Link the appropriate template to the host as shown below.

<p align="center">
  <img src="images/zabbix-host-template.png" alt="Zabbix: link template to host" width="700">
</p>

<sub>Figura N.01: Zabbix Host configuration screen showing how to link the "Inclinometer" template to a host and assign the host group.</sub>

## Links

[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/roberto-carlos-toapanta-g/)

[![twitter](https://img.shields.io/badge/twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/rotoapanta)
