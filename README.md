# serial-tilt-zbx

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Este proyecto lee datos de inclinómetros y pluviómetros desde puertos serie, los procesa y los envía a un servidor Zabbix para su monitoreo.

## Características

- Lectura concurrente de múltiples puertos serie.
- Procesamiento y parseo de datos en tiempo real.
- Envío de datos a Zabbix para monitoreo.
- Logging robusto con rotación de archivos.
- Manejo de errores y reconexión automática.
- Configuración externalizada en formato JSON.
- Pruebas unitarias para asegurar la calidad del código.

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/serial-tilt-zbx.git
   cd serial-tilt-zbx
   ```

2. (Opcional pero recomendado) Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

3. **Instala el agente de Zabbix:** Este proyecto utiliza el comando `zabbix_sender` para enviar datos a Zabbix. Asegúrate de que el agente de Zabbix esté instalado en el sistema que ejecuta este script. Puedes encontrar las instrucciones de instalación para tu sistema operativo en la [documentación oficial de Zabbix](https://www.zabbix.com/download_agents).

4. Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. **Configura los puertos serie:** Edita el archivo `config.json` para definir los puertos serie que quieres monitorear.

2. **Ejecuta la aplicación:**
   ```bash
   python main.py
   ```

3. **Revisa los logs:** Los logs se guardarán en el archivo `app.log`.

## Pruebas

Para ejecutar las pruebas unitarias, usa el siguiente comando:

```bash
python -m unittest discover tests
```