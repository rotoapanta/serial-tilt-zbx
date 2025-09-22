"""Concurrent serial port readers with retry limits and auto re-enable.

This module:
- Creates a thread per serial port from configuration.
- Reads data continuously and passes raw bytes to the data processor.
- Handles errors with a configurable retry policy (global and per-port):
  - max attempts, delay between attempts, and on-fail action
    (keep retrying | disable thread | stop app).
- Maintains a supervisor that probes disabled ports periodically and
  re-enables them when available.

Configuration (config.json):
- serial_ports: list of port dicts (port, baudrate, bytesize, parity, stopbits, timeout).
  Optional per-port overrides: max_retries, retry_delay, on_fail.
- serial_retry: { max_attempts, delay_seconds, on_fail } defaults for retries.
- serial_supervisor: { auto_reenable, reenable_interval_seconds } controls the supervisor.
"""

import logging
import serial
import threading
import time

from config.serial_config import SERIAL_PORTS
from config.app_config import APP_CONFIG
from utils.data_processor import process_data

# Supervisor state for disabled ports
_disabled_ports_lock = threading.Lock()
DISABLED_PORTS = {}


def _mark_port_disabled(port_config, reason: str = "") -> None:
    """Record a port as disabled for supervisor to attempt re-enable later."""
    logger = logging.getLogger(__name__)
    with _disabled_ports_lock:
        DISABLED_PORTS[port_config["port"]] = {
            "config": dict(port_config),
            "reason": reason,
            "ts": time.time(),
        }
    logger.warning(f"Port {port_config['port']} marked as disabled. Reason: {reason}")


def read_serial_port(port_config, stop_event=None):
    """Read from a single serial port in a loop with configurable retries.

    Opens the port, reads line-by-line, and dispatches to `process_data`.
    On open/read error, applies retry policy derived from:
    - Per-port overrides in `port_config`: max_retries, retry_delay, on_fail.
    - Global defaults in `APP_CONFIG['serial_retry']` when overrides are absent.

    Behavior:
    - Attempts counter resets after a successful open.
    - on_fail:
      - 'keep_retrying': continue retrying indefinitely after reaching max.
      - 'disable'/'disable_thread'/'stop_thread': mark port disabled and exit this thread.
      - 'stop_app'/'exit_app'/'exit': signal graceful app shutdown (or exit if no stop_event).
    - Disabled ports are tracked for possible re-enabling by the supervisor.

    Args:
        port_config (dict): Serial parameters; may include retry overrides.
        stop_event (threading.Event | None): Optional shared stop signal.

    Returns:
        None
    """
    logger = logging.getLogger(__name__)
    port_name = port_config['port']

    # Retry configuration: per-port override, else app-wide defaults
    retry_cfg = APP_CONFIG.get("serial_retry", {}) if isinstance(APP_CONFIG, dict) else {}
    default_max_retries = int(retry_cfg.get("max_attempts", 0) or 0)  # 0 means infinite
    default_retry_delay = int(retry_cfg.get("delay_seconds", 5) or 5)
    default_on_fail = str(retry_cfg.get("on_fail", "keep_retrying"))

    max_retries = int(port_config.get("max_retries", default_max_retries) or 0)
    retry_delay = int(port_config.get("retry_delay", default_retry_delay) or default_retry_delay)
    on_fail = str(port_config.get("on_fail", default_on_fail) or default_on_fail).lower()

    attempts = 0

    while stop_event is None or not stop_event.is_set():
        try:
            with serial.Serial(
                port=port_config["port"],
                baudrate=port_config["baudrate"],
                bytesize=port_config["bytesize"],
                parity=port_config["parity"],
                stopbits=port_config["stopbits"],
                timeout=port_config["timeout"],
            ) as ser:
                logger.info(f"Successfully opened port {port_name}")
                attempts = 0  # reset attempts after a successful open
                while stop_event is None or not stop_event.is_set():
                    raw_bytes = ser.readline()
                    if stop_event and stop_event.is_set():
                        break
                    if raw_bytes:
                        process_data(raw_bytes, port_name)
        except serial.SerialException as e:
            attempts += 1
            logger.error(
                f"Error with port {port_name}: {e} (attempt {attempts}{'/' + str(max_retries) if max_retries > 0 else ''})"
            )
            if max_retries > 0 and attempts >= max_retries:
                if on_fail in ("stop_app", "exit_app", "exit"):
                    logger.critical(f"Max retries reached for {port_name}. Stopping application as configured.")
                    if stop_event is not None:
                        stop_event.set()
                        break
                    else:
                        raise SystemExit(1)
                elif on_fail in ("disable", "disable_thread", "stop_thread"):
                    logger.error(f"Max retries reached for {port_name}. Disabling this port's reader thread.")
                    _mark_port_disabled(port_config, reason=str(e))
                    break
                else:
                    logger.warning(
                        f"Max retries reached for {port_name}. Continuing to retry indefinitely as configured."
                    )
                    # fall through to wait
            logger.info(f"Retrying to connect to {port_name} in {retry_delay} seconds...")
            if stop_event and stop_event.wait(retry_delay):
                break
        except Exception as e:
            attempts += 1
            logger.critical(f"An unexpected error occurred on port {port_name}: {e}")
            if max_retries > 0 and attempts >= max_retries:
                if on_fail in ("stop_app", "exit_app", "exit"):
                    logger.critical(f"Max retries reached for {port_name} after unexpected error. Stopping app.")
                    if stop_event is not None:
                        stop_event.set()
                        break
                    else:
                        raise SystemExit(1)
                elif on_fail in ("disable", "disable_thread", "stop_thread"):
                    logger.error(f"Max retries reached for {port_name} after unexpected error. Disabling thread.")
                    _mark_port_disabled(port_config, reason=str(e))
                    break
                else:
                    logger.warning(
                        f"Max retries reached for {port_name} after unexpected error. Continuing to retry indefinitely."
                    )
            logger.info(f"Retrying to connect to {port_name} in {retry_delay} seconds...")
            if stop_event and stop_event.wait(retry_delay):
                break

def start_serial_readers(stop_event=None):
    """Start reader threads for all configured ports and the supervisor.

    - Spawns a daemon thread per entry in `SERIAL_PORTS` running `read_serial_port`.
    - Starts a supervisor daemon that periodically attempts to reopen ports
      that were disabled after exceeding retry limits.

    Supervisor configuration via `APP_CONFIG['serial_supervisor']`:
    - auto_reenable (bool, default True): enable/disable automatic re-enabling.
    - reenable_interval_seconds (int, default 30): probe interval in seconds.

    Keeps the process alive until `stop_event` is set or a KeyboardInterrupt occurs.
    """
    logger = logging.getLogger(__name__)
    threads = []

    def _start_port_thread(pcfg):
        th = threading.Thread(target=read_serial_port, args=(pcfg, stop_event,))
        th.daemon = True  # Daemon threads will exit when the main program exits
        th.start()
        threads.append(th)

    for port_config in SERIAL_PORTS:
        _start_port_thread(port_config)

    # Start supervisor to re-enable disabled ports if configured
    sup_cfg = APP_CONFIG.get("serial_supervisor", {}) if isinstance(APP_CONFIG, dict) else {}
    auto_reenable = bool(sup_cfg.get("auto_reenable", True))
    reenable_interval = int(sup_cfg.get("reenable_interval_seconds", 30) or 30)

    def _supervisor_loop():
        s_logger = logging.getLogger(__name__)
        if not auto_reenable:
            s_logger.info("Serial supervisor auto_reenable disabled by configuration.")
        while stop_event is None or not stop_event.is_set():
            if auto_reenable:
                with _disabled_ports_lock:
                    disabled_items = list(DISABLED_PORTS.items())
                for port_name, meta in disabled_items:
                    cfg = meta.get("config", {})
                    try:
                        with serial.Serial(
                            port=cfg["port"],
                            baudrate=cfg["baudrate"],
                            bytesize=cfg["bytesize"],
                            parity=cfg["parity"],
                            stopbits=cfg["stopbits"],
                            timeout=cfg["timeout"],
                        ) as ser:
                            s_logger.info(f"Port re-enabled {port_name}")
                            with _disabled_ports_lock:
                                DISABLED_PORTS.pop(port_name, None)
                            _start_port_thread(cfg)
                    except Exception:
                        # Still unavailable; will retry on next interval
                        pass
            if stop_event and stop_event.wait(reenable_interval):
                break
            if stop_event is None:
                time.sleep(reenable_interval)

    supervisor_thread = threading.Thread(target=_supervisor_loop)
    supervisor_thread.daemon = True
    supervisor_thread.start()
    threads.append(supervisor_thread)

    try:
        if stop_event is None:
            # Keep the main thread alive, allowing daemon threads to run
            # and to catch KeyboardInterrupt gracefully.
            for thread in threads:
                thread.join()
        else:
            # Wait until a stop is requested
            while not stop_event.is_set():
                time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("Stopping serial port readers...")
        if stop_event is not None:
            stop_event.set()
    finally:
        logger.info("Joining serial port reader threads...")
        for thread in threads:
            thread.join(timeout=2)
