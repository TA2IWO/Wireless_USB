# 🔌 Wireless USB Bridge

**Raspberry Pi Zero 2 W · Raspberry Pi OS Lite · VirtualHere**

> This setup begins **after connecting to the Raspberry Pi via SSH** using PuTTY. Run the commands in order.

---

## 🚀 Installation

### 1. System Update

Updates the operating system and installs the packages required for the Wi-Fi meter.

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y curl wget nano iw python3-gpiozero python3-lgpio
```

Reboots the Raspberry Pi to apply the updates.

```bash
sudo reboot
```

*Reconnect using PuTTY after the reboot.*

### 2. Wi-Fi Meter Software

Opens the Python file where the Wi-Fi meter code will be saved.

```bash
nano ~/wifi_meter.py
```

Paste the **entire code** from [`[wifi_meter.py](https://github.com/TA2IWO/Wireless_USB/blob/main/Wi-Fi_meter.py)`](./wifi_meter.py) into the editor, then save with **Ctrl+O → Enter → Ctrl+X**.

Runs the code to verify that the Wi-Fi signal strength is correctly displayed on the 8 LEDs.

```bash
sudo python3 ~/wifi_meter.py
```

*Stop the test with **Ctrl+C**.*

### 3. VirtualHere USB Server

Installs VirtualHere using its official installation script and enables its automatic startup service.

```bash
cd ~
curl -fsSL https://raw.githubusercontent.com/virtualhere/script/main/install_server | sudo sh
```

Verifies that the VirtualHere service is running.

```bash
systemctl is-active virtualhere.service
```

*Expected output: `active`.*

### 4. Automatic Startup

Copies the Wi-Fi meter code to a permanent system directory.

```bash
sudo install -m 644 ~/wifi_meter.py /usr/local/bin/wifi_meter.py
```

Creates a service that starts the LED indicator after the Wi-Fi connection and VirtualHere service are ready.

```bash
sudo tee /etc/systemd/system/wifi-meter.service > /dev/null <<'EOF_SERVICE'
[Unit]
Description=Wi-Fi Signal Meter
Requires=virtualhere.service
Wants=network-online.target
After=virtualhere.service network-online.target

[Service]
Type=simple
ExecStartPre=/bin/sh -c 'until iw dev wlan0 link 2>/dev/null | grep -q "Connected to"; do sleep 2; done'
ExecStart=/usr/bin/python3 /usr/local/bin/wifi_meter.py
Restart=always
RestartSec=3
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF_SERVICE
```

Registers the service with the system and enables it to start automatically on subsequent boots.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now wifi-meter.service
```

Checks that both services are running.

```bash
systemctl is-active virtualhere.service wifi-meter.service
```

*Expected output: two lines showing `active`.*

### 5. Enable Read-Only Mode for the SD Card

Opens the Raspberry Pi configuration menu to help protect the SD card against unexpected power loss.

```bash
sudo raspi-config
```

Under **Performance Options → Overlay File System**, select:

- **Enable Overlay File System:** `Yes`
- **Write-protect boot partition:** `Yes`
- **Finish → Reboot**

> **Important:** Enable overlay mode only after installation and testing are complete. File changes made in this mode do not persist after a reboot; it reduces, but does not entirely eliminate, the risk of SD card corruption.

### 6. Final Verification

Checks that both services are running and the read-only overlay filesystem is active after reboot.

```bash
systemctl is-active virtualhere.service wifi-meter.service
findmnt -no FSTYPE /
```

*Expected output: `active`, `active`, `overlay`.*

---

## 💻 Windows Connection

Install [VirtualHere Client](https://www.virtualhere.com/usb_client_software) on Windows, connect to the same network, and double-click the USB device under the Raspberry Pi server.

---

<sub>**Note:** This setup uses the `wlan0` Wi-Fi interface and the GPIO order shown in the wiring diagram (`5, 6, 13, 12, 26, 16, 20, 21`). If a different network interface is used, update the Wi-Fi meter code and service configuration accordingly.</sub>
