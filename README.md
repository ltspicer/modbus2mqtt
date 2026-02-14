### This script receives data from an "RS485 to LAN/WIFI" converter and forwards it to another device via MQTT.

### Dieses Script empfängt Daten von einem "RS485 zu LAN/WIFI" Converter und sendet diese per MQTT an ein anderes Gerät weiter.

---------------------------------------

My configuration (Example):

- ioBroker (with MQTT adapter) in a Proxmox LXC
- Waveshare RS485 TO Wifi/ETH Converter (setting must be “**Transparent**” and **not** “modbus TCP <=> modbus RTU”)
- SOFAR HYD20KTL-3PH inverter

The desired data points and settings are entered in **config.yaml**.

Script can be stored in its own LXC:

**/opt/modbus-mqtt/modbus_tcp_rtu.py**

The **config.yaml** file is stored here:

**/opt/modbus-mqtt/config.yaml**

In **/etc/systemd/system/modbus-mqtt.service** (modbus-mqtt.service must be recreated)

```
[Unit]
Description=Modbus RTU over TCP to MQTT Gateway
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/modbus-mqtt
ExecStart=/usr/bin/env python3 /opt/modbus-mqtt/modbus_tcp_rtu.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

When everything is ready, enter:

```
sudo systemctl daemon-reload
sudo systemctl enable modbus-mqtt.service
sudo systemctl start modbus-mqtt.service
```

The data is now sent to ioBroker via MQTT.

The data point then looks something like this:

**mqtt.0.modbus.inverter.register.{register-address_name_description}**

![Screenshot](https://github.com/ltspicer/modbus2mqtt/blob/main/grafik1.png)

The script restarts automatically after a change to config.yaml.

It can be restarted manually as follows:

**systemctl restart modbus-mqtt.service**

My Waveshare:

![Screenshot](https://github.com/ltspicer/modbus2mqtt/blob/main/rs485toLAN_WIFI.png)

---------------------------------------

Meine Konfiguration (Beispiel):

- ioBroker (mit MQTT Adapter) in einem Proxmox LXC
- Waveshare RS485 TO Wifi/ETH Converter (Einstellung muss "**Transparent**" sein und **nicht** "modbus TCP <=> modbus RTU")
- SOFAR HYD20KTL-3PH Wechselrichter

Die gewünschten Datenpunkte und Einstellungen werden in der **config.yaml** eingegeben.

Script kann in einem eigenen LXC gespeichert werden:

**/opt/modbus-mqtt/modbus_tcp_rtu.py**

Die **config.yaml** Datei hier speichern:

**/opt/modbus-mqtt/config.yaml**

In der **/etc/systemd/system/modbus-mqtt.service** (modbus-mqtt.service muss neu erstellt werden)

```
[Unit]
Description=Modbus RTU over TCP to MQTT Gateway
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/modbus-mqtt
ExecStart=/usr/bin/env python3 /opt/modbus-mqtt/modbus_tcp_rtu.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Wenn alles fertig ist, eingeben:

```
sudo systemctl daemon-reload
sudo systemctl enable modbus-mqtt.service
sudo systemctl start modbus-mqtt.service
```

Die Daten werden nun per MQTT an den ioBroker gesendet.

Der Datenpunkt sieht dann etwa so aus:

**mqtt.0.modbus.inverter.register.{Registeradresse_name_description}**

![Screenshot](https://github.com/ltspicer/modbus2mqtt/blob/main/grafik1.png)

Das Script startet nach einer Änderung der config.yaml automatisch neu.

Von Hand kann es so neu gestartet werden:

**systemctl restart modbus-mqtt.service**

Mein Waveshare:

![Screenshot](https://github.com/ltspicer/modbus2mqtt/blob/main/rs485toLAN_WIFI.png)

