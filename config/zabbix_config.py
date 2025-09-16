"""Provides Zabbix server connection details.

This module defines the constants used by `zabbix_sender.py` to connect
to the Zabbix server. It specifies the server's address and the trapper port.
"""

# The IP address or hostname of your Zabbix server or proxy.
ZABBIX_SERVER = "192.168.1.143"

# The port of your Zabbix trapper (default is 10051).
ZABBIX_PORT = 10051
