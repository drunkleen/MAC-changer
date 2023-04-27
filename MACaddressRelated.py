import subprocess, string, random
import regex as re
import platform


class Linux:
    def __init__(self):
        self.hexdigits = ''.join(set(string.hexdigits.upper()))
        self.macaddress_string = ''

    def generate_random_mac_address(self):
        for i in range(6):
            for j in range(2):
                self.macaddress_string += random.choice('02468ACE') if i == 0 else \
                    random.choice(self.hexdigits)
            self.macaddress_string += ':'
        return self.macaddress_string

    def change_mac_address(self, interface, new_mac):
        subprocess.check_output(f'ifconfig {interface} down', shell=True)
        subprocess.check_output(f'ifconfig {interface} hw ether {new_mac}', shell=True)
        subprocess.check_output(f'ifconfig {interface} up', shell=True)


class Windows:
    def __init__(self):
        self.mac_address = None
        self.hexdigits = None
        self.adapter_index = None
        self.network_interface_reg_path = r"HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}"
        self.transport_name_regex = re.compile("{.+}")
        self.mac_address_regex = re.compile(r"([A-Z0-9]{2}[:-]){5}([A-Z0-9]{2})")
        self.connected_adapters_mac = []

    def get_random_mac_address(self):
        self.hexdigits = ''.join(set(string.hexdigits.upper()))
        return random.choice(self.hexdigits) + random.choice("24AE") + "".join(
            random.sample(self.hexdigits, k=10))

    def mac_cleaner(self, mac):
        return "".join(c for c in mac if c in string.hexdigits).upper()

    def get_connected_adapters_mac_address(self):
        for potential_mac in subprocess.check_output("getmac").decode().splitlines():
            self.mac_address = self.mac_address_regex.search(potential_mac)
            # parse the transport name from the line
            transport_name = self.transport_name_regex.search(potential_mac)
            if self.mac_address and transport_name:
                # if a MAC and transport name are found, add them to our list
                self.connected_adapters_mac.append((self.mac_address.group(), transport_name.group()))
        return self.connected_adapters_mac

    def get_user_adapter_choice(self, connected_adapters_mac):
        for i, option in enumerate(connected_adapters_mac):
            print(f"#{i}: {option[0]}, {option[1]}")
        if len(connected_adapters_mac) <= 1:
            return connected_adapters_mac[0]
        try:
            choice = int(input("Please choose the interface you want to change the MAC address:"))
            return connected_adapters_mac[choice]
        except:
            print("Not a valid choice, quitting...")
            exit()

    def change_mac_address(self, adapter_transport_name, new_mac_address):

        output = subprocess.check_output(f"reg QUERY " + self.network_interface_reg_path.replace("\\\\", "\\")).decode()
        for interface in re.findall(rf"{self.network_interface_reg_path}\\\d+", output):
            self.adapter_index = int(interface.split("\\")[-1])
            interface_content = subprocess.check_output(f"reg QUERY {interface.strip()}").decode()
            if adapter_transport_name in interface_content:
                changing_mac_output = subprocess.check_output(
                    f"reg add {interface} /v NetworkAddress /d {new_mac_address} /f").decode()
                print(changing_mac_output)
                break
        return self.adapter_index

    def disable_adapter(self, adapter_index):
        disable_output = subprocess.check_output(
            f"wmic path win32_networkadapter where index={adapter_index} call disable").decode()
        return disable_output

    def enable_adapter(self, adapter_index):
        enable_output = subprocess.check_output(
            f"wmic path win32_networkadapter where index={adapter_index} call enable").decode()
        return enable_output
