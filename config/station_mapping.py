"""Provides a mapping from numeric station IDs to human-readable station names.

This module defines the `STATION_NAMES` dictionary, which is used to translate
the station number received in a data frame into a descriptive name. This name
is then used for logging, local data storage paths, and as a base for the
Zabbix host name.
"""

STATION_NAMES = {
    1: "VC1",
    2: "BILBAO",
    3: "RETU",
    4: "CHONTAL",
    5: "GPCAM",
    6: "CAYR",
    7: "CAYM",
    8: "PONDOA",
    9: "COTOR",
    10: "MANDUR",    # cambiar en estacion
    11: "GGPA",
    # Add other station mappings here
}
