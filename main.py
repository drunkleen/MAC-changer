from getmac import get_mac_address
import platform
from MACaddressRelated import Windows, Linux

if __name__ == '__main__':
    import argparse

    varOS = platform.system()
    print(f"[*] OS: {varOS}\n[*] OS release: {platform.release()}")

    if varOS.lower() == "linux":
        linux = Linux()
        parser = argparse.ArgumentParser(description="Linux MAC Changer")
        parser.add_argument('interface', help='The network interface name on Linux')
        parser.add_argument('-r', '--random', action='store_true',
                            help='generate random MAC')
        parser.add_argument('-m', '--mac', help='special MAC')
        args = parser.parse_args()
        iface = args.interface
        new_mac_address = linux.generate_random_mac_address() if args.random else args.mac
        print('[*] Old MAC address:', get_mac_address())
        linux.change_mac_address(iface, new_mac_address)
        print('[+] New MAC address:', get_mac_address())

    elif varOS.lower() == "windows":
        windows = Windows()
        parser = argparse.ArgumentParser(description='Windows MAC Changer')
        parser.add_argument('-r', '--random', action='store_true', help='Whether to generate random Mac address')
        parser.add_argument('-m', '--mac', help='The MAC address to generate')
        args = parser.parse_args()

        new_mac_address = windows.get_random_mac_address() if args.random else\
            windows.mac_cleaner(args.mac)

        connected_adapters_mac = windows.get_connected_adapters_mac_address()
        old_mac_address, target_transport_name = windows.get_user_adapter_choice(connected_adapters_mac)
        print('[*] Old MAC address:', old_mac_address)
        adapter_index = windows.change_mac_address(target_transport_name, new_mac_address)
        print("[+] Changed to:", new_mac_address)
        windows.disable_adapter(adapter_index)
        print("[+] Adapter is disabled")
        windows.enable_adapter(adapter_index)
        print("[+] Adapter is enabled")
