#!/bin/bash
# Script para configurar el entorno del proyecto en una Raspberry Pi,
# incluyendo la instalación de dependencias del sistema.

# Detiene el script si cualquier comando falla
set -e

echo "--- Iniciando la configuración completa del proyecto serial-tilt-zbx ---"

# 1. Verificar e instalar dependencias del sistema
echo "[Paso 1/4] Verificando dependencias del sistema (python3, python3-venv, git)..."

# Lista de paquetes requeridos
PACKAGES="python3 python3-venv git"
PACKAGES_TO_INSTALL=""

for pkg in $PACKAGES; do
    # Se usa dpkg-query para una verificación robusta en sistemas Debian/Raspberry Pi OS
    if ! dpkg-query -W -f='${Status}' $pkg 2>/dev/null | grep -q "install ok installed"; then
        PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL $pkg"
    fi
done

if [ -n "$PACKAGES_TO_INSTALL" ]; then
    echo "   Se instalarán los siguientes paquetes del sistema: $PACKAGES_TO_INSTALL"
    echo "   Se requerirá tu contraseña (sudo) para continuar."
    sudo apt-get update
    sudo apt-get install -y $PACKAGES_TO_INSTALL
else
    echo "   Todas las dependencias del sistema ya están instaladas."
fi

# 2. Crear el entorno virtual
echo "[Paso 2/4] Creando entorno virtual 'venv'..."
# Se asegura de que el venv se cree con el usuario que ejecuta el script, no como root
python3 -m venv venv

# 3. Instalar dependencias de Python
echo "[Paso 3/4] Instalando dependencias de Python desde requirements.txt..."
# Se usa el pip del entorno virtual directamente para evitar problemas
./venv/bin/pip install -r requirements.txt

# 4. Dar permisos de ejecución al script
echo "[Paso 4/4] Asegurando permisos de ejecución para este script..."
chmod +x setup_pi.sh

echo ""
echo "--- ¡Configuración completada! ---"
echo ""
echo "Pasos a seguir:"
echo "1. Activa el entorno virtual con el comando:"
echo "   source venv/bin/activate"
echo ""
echo "2. ¡IMPORTANTE! Edita los archivos de configuración (especialmente 'config/serial_config.py') para que coincidan con el hardware de tu Raspberry Pi (ej. puerto serie '/dev/ttyUSB0')."
echo ""
echo "3. Una vez configurado, ejecuta la aplicación con:"
echo "   python main.py"
echo ""
echo "NOTA: Si recibes un error de 'Permission denied' al acceder al puerto serie, ejecuta:"
echo "sudo usermod -a -G dialout $USER"
echo "Y luego cierra sesión y vuelve a iniciarla."
