"""Zabbix sending utilities with batching, retries/backoff, and preflight.

This module provides robust functions to send data points to a Zabbix server
using the `zabbix_sender` command-line utility.

Enhancements:
- Batch sending per host using input file (-i) to reduce overhead
- Retries with exponential backoff on failure/timeouts
- Optional on-disk spool for failed batches and automatic draining
- Configurable timeout, retries, verbosity and spool directory via config.json
  with environment variable overrides
- Preflight checks on startup: presence of zabbix_sender and TCP connectivity
"""
from __future__ import annotations

import os
import logging
import tempfile
import subprocess
import time
import shutil
import socket
from typing import List, Tuple

from config.app_config import APP_CONFIG
from config.zabbix_config import ZABBIX_SERVER, ZABBIX_PORT

logger = logging.getLogger(__name__)


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _get_sender_options():
    """Retrieve zabbix_sender options from config and environment.

    Environment overrides (take precedence over config):
      - ZBX_SENDER_TIMEOUT (int seconds)
      - ZBX_SENDER_RETRIES (int)
      - ZBX_SENDER_VERBOSE (bool: 0/1, true/false, yes/no)
      - ZBX_SPOOL_DIR (path)
    """
    cfg = APP_CONFIG.get("zabbix_sender", {}) if isinstance(APP_CONFIG, dict) else {}

    timeout = int(os.getenv("ZBX_SENDER_TIMEOUT", cfg.get("timeout", 10)))
    retries = int(os.getenv("ZBX_SENDER_RETRIES", cfg.get("retries", 3)))
    verbose = _env_bool("ZBX_SENDER_VERBOSE", bool(cfg.get("verbose", False)))
    spool_dir = os.getenv("ZBX_SPOOL_DIR", cfg.get("spool_dir", "./zbx_spool"))

    return {
        "timeout": timeout,
        "retries": retries,
        "verbose": verbose,
        "spool_dir": spool_dir,
    }


def preflight_check():
    """Run startup checks and attempt draining local spool.

    - Verify `zabbix_sender` binary is available in PATH.
    - Verify TCP connectivity to Zabbix server/port.
    - Attempt to drain local spool directory if present.
    """
    opts = _get_sender_options()

    # Check binary
    if shutil.which("zabbix_sender") is None:
        logger.warning("'zabbix_sender' binary not found in PATH. Data sending will fail until installed.")
    else:
        logger.info("zabbix_sender binary found.")

    # Check connectivity
    try:
        with socket.create_connection((ZABBIX_SERVER, int(ZABBIX_PORT)), timeout=opts["timeout"]) as _:
            logger.info(f"Connectivity to Zabbix {ZABBIX_SERVER}:{ZABBIX_PORT} OK.")
    except Exception as e:
        logger.warning(f"Cannot connect to Zabbix {ZABBIX_SERVER}:{ZABBIX_PORT}: {e}. Will retry upon sends.")

    # Try draining spool
    try:
        drain_spool()
    except Exception as e:
        logger.warning(f"Failed draining spool at startup: {e}")


def _run_sender_with_retries(file_path: str, verbose: bool, timeout: int, retries: int) -> bool:
    """Execute zabbix_sender with retries and exponential backoff."""
    base_cmd = [
        "zabbix_sender",
        "-z", str(ZABBIX_SERVER),
        "-p", str(ZABBIX_PORT),
        "-i", file_path,
    ]
    if verbose:
        base_cmd.append("-vv")

    attempt = 0
    while True:
        try:
            result = subprocess.run(base_cmd, capture_output=True, text=True, check=True, timeout=timeout)
            if result.stdout:
                logger.debug(f"zabbix_sender stdout: {result.stdout.strip()}")
            if result.stderr:
                logger.debug(f"zabbix_sender stderr: {result.stderr.strip()}")
            return True
        except FileNotFoundError:
            logger.error("'zabbix_sender' command not found. Install it and ensure it is in PATH.")
            return False
        except subprocess.TimeoutExpired:
            logger.error("zabbix_sender command timed out.")
        except subprocess.CalledProcessError as e:
            logger.error("zabbix_sender failed. Output:")
            if e.stdout:
                logger.error(f"  stdout: {e.stdout.strip()}")
            if e.stderr:
                logger.error(f"  stderr: {e.stderr.strip()}")

        if attempt >= retries:
            return False
        backoff = min(60, 2 ** attempt)
        logger.info(f"Retrying zabbix_sender in {backoff}s (attempt {attempt + 1}/{retries})...")
        time.sleep(backoff)
        attempt += 1


def _send_lines_batch(lines: List[str], allow_spool_on_fail: bool = True) -> bool:
    """Send a batch of lines using zabbix_sender -i <tempfile>.

    Each line must be in the format: "<host> <key> <value>".
    """
    if not lines:
        return True

    opts = _get_sender_options()

    # Write lines to a temporary file for zabbix_sender -i
    tmp_file = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False) as tf:
            tmp_file = tf.name
            tf.write("\n".join(lines) + "\n")

        ok = _run_sender_with_retries(tmp_file, opts["verbose"], opts["timeout"], opts["retries"])
        if ok:
            # Success: log a concise confirmation
            try:
                logger.info(f"Sent {len(lines)} metrics to Zabbix {ZABBIX_SERVER}:{ZABBIX_PORT}.")
            except Exception:
                pass
            # On success, try drain spool as well
            try:
                drain_spool()
            except Exception as e:
                logger.debug(f"Drain spool after success failed: {e}")
            return True
        else:
            if allow_spool_on_fail:
                _spool_lines(lines)
            return False
    finally:
        if tmp_file and os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except OSError:
                pass


def _spool_lines(lines: List[str]) -> None:
    opts = _get_sender_options()
    spool_dir = opts["spool_dir"]
    os.makedirs(spool_dir, exist_ok=True)

    try:
        with tempfile.NamedTemporaryFile("w", delete=False, dir=spool_dir, prefix="zbx_", suffix=".spool") as sf:
            sf.write("\n".join(lines) + "\n")
            path = sf.name
        logger.warning(f"Batch spooled to disk: {path}")
    except Exception as e:
        logger.error(f"Failed to write spool file: {e}")


def drain_spool() -> None:
    """Attempt to resend any spooled batches from disk.

    Stops on first failure to avoid tight loops.
    """
    opts = _get_sender_options()
    spool_dir = opts["spool_dir"]
    if not os.path.isdir(spool_dir):
        return

    entries = sorted(
        (os.path.join(spool_dir, f) for f in os.listdir(spool_dir) if f.endswith(".spool")),
        key=lambda p: os.path.getmtime(p),
    )

    for path in entries:
        try:
            with open(path, "r") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            ok = _send_lines_batch(lines, allow_spool_on_fail=False)
            if ok:
                try:
                    os.remove(path)
                    logger.info(f"Sent and removed spooled batch: {path}")
                except OSError as e:
                    logger.warning(f"Sent spooled batch but could not remove {path}: {e}")
            else:
                logger.warning(f"Failed to send spooled batch {path}. Will retry later.")
                break  # stop draining on first failure
        except Exception as e:
            logger.error(f"Error processing spool file {path}: {e}")


def _build_host_lines(host_name: str, items: List[Tuple[str, object]]) -> List[str]:
    lines: List[str] = []
    for key, value in items:
        lines.append(f"{host_name} {key} {value}")
    return lines


def send_inclinometer_to_zabbix(data: dict) -> None:
    """Batch-send inclinometer data points for a given station to Zabbix.

    Groups metrics per host and sends them in one zabbix_sender call using -i.
    """
    try:
        base_station_name = data["station_name"]
        incli_data = data["inclinometer"]
        host_name = f"{base_station_name}_IN"

        key_map = APP_CONFIG.get("zabbix_keys", {}).get("inclinometer", {})
        items: List[Tuple[str, object]] = []
        for data_key, value in incli_data.items():
            zabbix_key = key_map.get(data_key)
            if zabbix_key is not None:
                items.append((zabbix_key, value))
            else:
                logger.warning(f"No Zabbix key mapping for inclinometer data '{data_key}'.")

        lines = _build_host_lines(host_name, items)
        _send_lines_batch(lines)
    except KeyError as e:
        logger.error(f"Error preparing inclinometer data for Zabbix: Missing key {e}")


def send_pluviometer_to_zabbix(data: dict) -> None:
    """Batch-send pluviometer data points for a given station to Zabbix.

    Groups metrics per host and sends them in one zabbix_sender call using -i.
    """
    try:
        base_station_name = data["station_name"]
        pluvio_data = data["pluviometer"]
        host_name = f"{base_station_name}_PL"

        key_map = APP_CONFIG.get("zabbix_keys", {}).get("pluviometer", {})
        items: List[Tuple[str, object]] = []
        for data_key, value in pluvio_data.items():
            zabbix_key = key_map.get(data_key)
            if zabbix_key is not None:
                items.append((zabbix_key, value))
            else:
                logger.warning(f"No Zabbix key mapping for pluviometer data '{data_key}'.")

        lines = _build_host_lines(host_name, items)
        _send_lines_batch(lines)
    except KeyError as e:
        logger.error(f"Error preparing pluviometer data for Zabbix: Missing key {e}")
