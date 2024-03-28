# pip install qrcode[pil]
import qrcode
import os
import re
import subprocess


def get_current_ssid():
    try:
        # Getting the current SSID using iwgetid
        result = subprocess.check_output(["iwgetid", "-r"]).decode().strip()
        return result
    except subprocess.CalledProcessError:
        print("Could not get current SSID.")
        return None


def get_ip_address():
    try:
        ip_info = subprocess.check_output(["ip", "addr", "show", "wlan0"]).decode()
        ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/', ip_info)
        if ip_match:
            return ip_match.group(1)
    except subprocess.CalledProcessError:
        return None


def get_wifi_credentials(ssid):
    config_path = f"/etc/NetworkManager/system-connections/{ssid}.nmconnection"
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            content = file.read()
            psk_match = re.search(r'^psk=(.*)', content, re.MULTILINE)
            if psk_match:
                return ssid, psk_match.group(1)
    return ssid, None


def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("/var/www/html/" + filename)


ssid = get_current_ssid()
if ssid:
    ssid, psk = get_wifi_credentials(ssid)
    ip_address = get_ip_address()
    data_to_encode = f"{ssid} {psk} {ip_address}"
    output_filename = "qr_code.png"
    generate_qr_code(data_to_encode, output_filename)
    print(f"QR code generated and saved as {output_filename}")
