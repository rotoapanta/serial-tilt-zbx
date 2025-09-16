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

# <p align="center">RSerial-Tilt-ZBX</p>


Este proyecto lee, procesa y envía datos de inclinómetros y pluviómetros desde puertos serie a un servidor Zabbix para su monitoreo en tiempo real.

## Características

- **Lectura Concurrente:** Monitorea múltiples puertos serie de forma simultánea.
- **Procesamiento de Datos:** Parsea tramas de datos específicas de los sensores.
- **Integración con Zabbix:** Utiliza `zabbix_sender` para enviar métricas a un servidor Zabbix.
- **Logging Robusto:** Registra la actividad de la aplicación, incluyendo errores, con rotación de archivos.
- **Configuración Flexible:** Gestiona la configuración de puertos y Zabbix a través de archivos externos.
- **Instalación Automatizada:** Incluye scripts para facilitar la configuración en Raspberry Pi.
- **Ejecución como Servicio:** Permite la instalación como un servicio `systemd` para operación continua.

## Requisitos del Sistema

Este proyecto está diseñado para sistemas operativos basados en Debian (como Raspberry Pi OS, Ubuntu, etc.). Antes de la instalación, asegúrate de que tu sistema tenga los siguientes paquetes. El script `setup_pi.sh` intentará instalarlos automáticamente.

- `python3`
- `python3-venv` (para la creación de entornos virtuales)
- `git` (para clonar el repositorio)
- `zabbix-sender` (para enviar datos a Zabbix)

---

## Implementación en Raspberry Pi (Recomendado)

Esta es la forma recomendada para poner el sistema en producción. Los scripts automatizan la instalación de dependencias y la configuración del servicio.

### 1. Preparación

- Clona este repositorio en tu Raspberry Pi:
  ```bash
  git clone https://github.com/tu-usuario/serial-tilt-zbx.git
  cd serial-tilt-zbx
  ```

### 2. Ejecutar el Script de Configuración

- Este script instalará las dependencias del sistema (como `python3-venv` y `zabbix-sender`) y las librerías de Python necesarias.
  ```bash
  chmod +x setup_pi.sh
  ./setup_pi.sh
  ```
  *Nota: El script podría solicitar tu contraseña (`sudo`) si necesita instalar paquetes del sistema.*

### 3. Configurar la Aplicación

- **¡MUY IMPORTANTE!** Edita los archivos de configuración para que coincidan con tu hardware y servidor.
  - `config/serial_config.py`: Ajusta el nombre de los puertos serie (ej. `/dev/ttyUSB0`).
  - `config/zabbix_config.py`: Define la dirección de tu servidor Zabbix.
  - `config/station_mapping.py`: Mapea los IDs de las estaciones a los nombres de host de Zabbix.

### 4. Instalar como un Servicio (Opcional pero Recomendado)

- Para que la aplicación se inicie automáticamente y se mantenga en ejecución, instálala como un servicio `systemd`.
  ```bash
  chmod +x install_service.sh
  ./install_service.sh
  ```
- El script generará un archivo `.service` y te mostrará los comandos exactos para moverlo, habilitarlo e iniciarlo. Sigue las instrucciones que aparecen en la terminal.

- **Para gestionar el servicio:**
  - **Ver estado:** `sudo systemctl status serial-tilt-zbx.service`
  - **Ver logs:** `journalctl -u serial-tilt-zbx.service -f`

---

## Instalación Manual (Entorno de Desarrollo)

Sigue estos pasos para una instalación manual en cualquier sistema Linux.

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/serial-tilt-zbx.git
   cd serial-tilt-zbx
   ```

2. **Instala `zabbix-sender`:**
   - En sistemas Debian/Ubuntu/Raspberry Pi OS:
     ```bash
     sudo apt-get update && sudo apt-get install zabbix-sender
     ```

3. **Crea un entorno virtual y activa:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Instala las dependencias de Python:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configura y ejecuta:**
   - Edita los archivos en el directorio `config/`.
   - Ejecuta la aplicación:
     ```bash
     python main.py
     ```

## Pruebas

Para ejecutar las pruebas unitarias, usa el siguiente comando desde el directorio raíz del proyecto:

```bash
python -m unittest discover tests
```
