#!/usr/bin/env python3

import socket
import struct
import time
import yaml
import logging
import paho.mqtt.client as mqtt
import os
import re

CONFIG_FILE = "/opt/modbus-mqtt/config.yaml"
LOG_FILE = "/var/log/modbus-mqtt.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logging.info("Starting modbus-mqtt with config from disk")

try:
    with open(CONFIG_FILE, "r") as f:
        cfg = yaml.safe_load(f)
except Exception as e:
    logging.error(f"Failed to load config: {e}")
    exit(1)

last_mtime = os.path.getmtime(CONFIG_FILE)

MODBUS_HOST = cfg["modbus"]["host"]
MODBUS_PORT = cfg["modbus"]["port"]
UNIT_ID = cfg["modbus"]["unit_id"]

MQTT_HOST = cfg["mqtt"]["host"]
MQTT_PORT = cfg["mqtt"]["port"]
BASE_TOPIC = cfg["mqtt"]["base_topic"]

POLL_INTERVAL = cfg["poll_interval"]
REGISTERS = cfg["registers"]

mqttc = mqtt.Client(client_id="modbus_mqtt_bridge", clean_session=True)

mqtt_user = cfg["mqtt"].get("username")
mqtt_pass = cfg["mqtt"].get("password")

if mqtt_user and mqtt_pass:
    mqttc.username_pw_set(mqtt_user, mqtt_pass)
elif mqtt_user or mqtt_pass:
    logging.warning("MQTT username or password missing. Authentication disabled.")
else:
    logging.info("No auth data found. Start without authentication")

mqttc.connect(MQTT_HOST, MQTT_PORT)
mqttc.loop_start()

# ---------------------------------------------------------
# Text bereinigen
# ---------------------------------------------------------

def sanitize(text):
    # Umlaute ersetzen
    text = (
        text.replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("Ä", "Ae")
            .replace("Ö", "Oe")
            .replace("Ü", "Ue")
            .replace("ß", "ss")
    )

    # Problematische Zeichen ersetzen
    text = text.replace("-", "_")
    text = text.replace(":", "_")

    # Erlaubt: A-Z, a-z, 0-9, _
    text = re.sub(r"[^A-Za-z0-9_]+", "_", text)

    # Mehrere Unterstriche zu einem machen
    text = re.sub(r"_+", "_", text)

    # Anfang/Ende säubern
    return text.strip("_")

# ---------------------------------------------------------
# CRC16 Modbus
# ---------------------------------------------------------

def crc16(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder="little")

# ---------------------------------------------------------
# RTU‑Frame senden über TCP
# ---------------------------------------------------------

def read_holding_registers_rtu_tcp(unit, address, count):
    # Build RTU frame: [unit][function][addr_hi][addr_lo][count_hi][count_lo][crc_lo][crc_hi]
    frame = bytearray()
    frame.append(unit)
    frame.append(0x03)  # Function code: Read Holding Registers
    frame += struct.pack(">HH", address, count)
    frame += crc16(frame)

    # TCP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect((MODBUS_HOST, MODBUS_PORT))
    s.send(frame)

    # Response
    response = s.recv(256)
    s.close()

    # Validate minimum length
    if len(response) < 5:
        raise Exception("Invalid response length")

    # Validate CRC
    data = response[:-2]
    crc_received = response[-2:]
    crc_calc = crc16(data)
    if crc_received != crc_calc:
        raise Exception("CRC mismatch")

    # Byte count
    byte_count = response[2]
    if byte_count != count * 2:
        raise Exception("Unexpected byte count")

    # Extract registers
    registers = []
    for i in range(count):
        hi = response[3 + i*2]
        lo = response[4 + i*2]
        registers.append((hi << 8) | lo)

    return registers

# ---------------------------------------------------------
# Poll‑Loop
# ---------------------------------------------------------

last_values = {}

while True:
    # Auto‑Reload wenn config.yaml geändert wurde
    current_mtime = os.path.getmtime(CONFIG_FILE)
    if current_mtime != last_mtime:
        logging.info("Config changed, restarting...")
        mqttc.loop_stop()
        exit(0)

    for reg in REGISTERS:
        addr = reg["addr"]
        reg_type = reg["type"]
        factor = reg["factor"]
        length = 2 if reg_type == "uint32" else 1

        try:
            regs = read_holding_registers_rtu_tcp(UNIT_ID, addr, length)

            if reg_type == "int16":
                value = struct.unpack(">h", struct.pack(">H", regs[0]))[0]
            elif reg_type == "uint16":
                value = regs[0]
            elif reg_type == "uint32":
                value = (regs[0] << 16) | regs[1]
            else:
                continue

            value *= factor

            # Nachkommastellen basierend auf config.yaml
            decimals = reg.get("decimals", None)
            if decimals is not None:
                value = round(value, decimals)

            # Beschreibung + Name in Topic einbauen
            name = reg.get("name", "")
            desc = reg.get("description", "")

            name_clean = sanitize(name)
            desc_clean = sanitize(desc)

            # Format: addr:name-description
            topic_suffix = str(addr)

            if name_clean:
                topic_suffix += f"_{name_clean}"

            if desc_clean:
                topic_suffix += f"_{desc_clean}"

            topic = f"{BASE_TOPIC}/register/{topic_suffix}"

            # Nur senden, wenn sich der Wert geändert hat
            if addr in last_values and last_values[addr] == value:
                continue  # Wert unverändert → nicht senden

            last_values[addr] = value
            mqttc.publish(topic, value)
            #logging.info(f"Published {topic} = {value}")

        except Exception as e:
            logging.error(f"Error reading register {addr}: {e}")

        time.sleep(0.2)

    time.sleep(POLL_INTERVAL)
