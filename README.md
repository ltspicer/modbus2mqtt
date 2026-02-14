Meine Konfiguration:

- ioBroker in einer Proxmox LXC (mit MQTT Adapter)
- Waveshare RS485 TO Wifi/ETH Converter (Einstellung: "Transparent")
- SOFAR HYD20KTL-3PH Wechselrichter

Die gewünschten Datenpunkte und Einstellungen werden in der config.yaml eingegeben.

Script hier gespeichert (in einem eigenen LXC):
/opt/modbus-mqtt/modbus_tcp_rtu.py

Die config.yaml Datei hier gespeichert:
/opt/modbus-mqtt/config.yaml

In der /etc/systemd/system/modbus-mqtt.service

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
