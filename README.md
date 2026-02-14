Meine Konfiguration (Beispiel):

- ioBroker in einer Proxmox LXC (mit MQTT Adapter)
- Waveshare RS485 TO Wifi/ETH Converter (Einstellung: "Transparent". NICHT: "modbus TCP <=> modbus RTU")
- SOFAR HYD20KTL-3PH Wechselrichter

Die gewünschten Datenpunkte und Einstellungen werden in der **config.yaml** eingegeben.

Script hier gespeichert (in einem eigenen LXC):

**/opt/modbus-mqtt/modbus_tcp_rtu.py**

Die **config.yaml** Datei hier gespeichert:

**/opt/modbus-mqtt/config.yaml**

In der **/etc/systemd/system/modbus-mqtt.service**

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


Das Script sollte nach Änderung der config.yaml automatisch neu starten 

Von Hand kann es so neu gestartet werden:

**systemctl restart modbus-mqtt.service**

Mein Waveshare:

![Screenshot](https://github.com/ltspicer/modbus2mqtt/blob/main/rs485toLAN_WIFI.png)

---------------------------------------

My configuration (Example):

- ioBroker in a Proxmox LXC (with MQTT adapter)
- Waveshare RS485 TO Wifi/ETH Converter (setting: “Transparent.” NOT: “modbus TCP <=> modbus RTU”)
- SOFAR HYD20KTL-3PH inverter

The desired data points and settings are entered in **config.yaml**.

Script stored here (in a separate LXC):

**/opt/modbus-mqtt/modbus_tcp_rtu.py**

The **config.yaml** file stored here:

**/opt/modbus-mqtt/config.yaml**

In **/etc/systemd/system/modbus-mqtt.service**

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


The script should restart automatically after changing config.yaml.

It can be restarted manually as follows:

**systemctl restart modbus-mqtt.service**

My Waveshare:

![Screenshot](https://github.com/ltspicer/modbus2mqtt/blob/main/rs485toLAN_WIFI.png)

