#!/bin/bash
# Script para crear e instalar el servicio systemd para la aplicación serial-tilt-zbx

set -e

# --- Configuración ---
SERVICE_NAME="serial-tilt-zbx"
# Obtener el directorio absoluto del proyecto y el nombre de usuario
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
USER=$(whoami)
PYTHON_EXEC="$PROJECT_DIR/venv/bin/python"
MAIN_SCRIPT="$PROJECT_DIR/main.py"

SERVICE_FILE="$SERVICE_NAME.service"

echo "--- Creando archivo de servicio para '$SERVICE_NAME' ---"

# Crear el contenido del archivo de servicio aquí
# Usamos EOF para manejar un bloque de texto de manera limpia
cat > $SERVICE_FILE <<EOF
[Unit]
Description=Servicio para leer datos de inclinómetro/pluviómetro y enviarlos a Zabbix
After=network.target

[Service]
# Usuario y grupo que ejecutará el servicio
User=$USER
Group=$(id -gn $USER)

# Directorio de trabajo del script
WorkingDirectory=$PROJECT_DIR

# Comando para iniciar el servicio
# Usamos el intérprete de Python del entorno virtual
ExecStart=$PYTHON_EXEC $MAIN_SCRIPT

# Política de reinicio
Restart=always
RestartSec=10s

# Configuración de logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

echo "Archivo de servicio '$SERVICE_FILE' creado con éxito."
echo ""
echo "--- Pasos para la instalación (requiere sudo) ---"
echo ""
echo "Por favor, ejecuta los siguientes comandos en tu Raspberry Pi para instalar y iniciar el servicio:"
echo ""
echo "1. Mover el archivo de servicio al directorio de systemd:"
echo -e "   \033[1;33msudo mv ~/$SERVICE_FILE /etc/systemd/system/$SERVICE_FILE\033[0m"
echo ""
echo "2. Recargar el demonio de systemd para que reconozca el nuevo servicio:"
echo -e "   \033[1;33msudo systemctl daemon-reload\033[0m"
echo ""
echo "3. Habilitar el servicio para que se inicie automáticamente en el arranque:"
echo -e "   \033[1;33msudo systemctl enable $SERVICE_NAME.service\033[0m"
echo ""
echo "4. Iniciar el servicio ahora mismo:"
echo -e "   \033[1;33msudo systemctl start $SERVICE_NAME.service\033[0m"
echo ""
echo "--- Comandos útiles para gestionar el servicio ---"
echo ""
echo "- Para ver el estado del servicio:"
echo -e "   \033[1;32msudo systemctl status $SERVICE_NAME.service\033[0m"
echo ""
echo "- Para ver los logs en tiempo real:"
echo -e "   \033[1;32mjournalctl -u $SERVICE_NAME.service -f\033[0m"
echo ""
echo "- Para detener el servicio:"
echo -e "   \033[1;32msudo systemctl stop $SERVICE_NAME.service\033[0m"
