import requests
import atexit
from time import sleep

import wpa_cli

def PortalSmash():
    smashing = False
    badnets_file = "badnets.log"

    def __init__(self):
        self.read_badnets()
        atexit.register(self.write_badnets)

    def read_badnets(self):
        with open(self.badnets_file, 'r') as f:
            self.badnets = [line.strip() for line in f.readlines()]

    def write_badnets(self):
        with open(self.badnets_file, 'w') as f:
            f.write('\n'.join(self.badnets))

    def check_conn(self, page="http://www.apple.com/library/test/success.html"):
        try:
            r = requests.get(page)
        except Exception as e:
            print("Requests exception: {}".format(repr(e))
            return None
        return r.text.lower() == "<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>".lower()
    
    def check_wifi(self):
        if self.badnet is not None:
            self.badnets.append(self.badnet)
            self.badnet = None
        status = wpa_cli.connection_status()
        state = status["wpa_state"]
        if state == "COMPLETED":
            return status
        else:
            print("Not connected, retrying!")
            wpa_cli.scan()
            sleep(5)
            avail_networks = wpa_cli.get_scan_results()
            for network in avail_networks:
                if network["bssid"] in self.badnets:
                    print("Avoiding bad network {}".format(network["bssid"]))
                    continue
                elif wpa_cli.is_open_network(network):
                    #Adding net network, gotta reset the smash counter
                    self.smash_counter = 0
                    id = wpa_cli.add_open_network(network)
                    wpa_cli.select_network(id)
                    print("Selected '{}'".format(network["ssid"]))
                    sleep(5)
                    print("Hope we got the IP now")
                    return
            return None

    def smash(self, net_info):
        print("Gotta smash that {}!".format(net_info))
        return False

    def loop(self):
        self.smashing = True
        print("Starting smashing!")
        while self.smashing:
            net_info = self.check_connect_wifi()
            if self.smash_counter == 3:
                bssid = net_info["bssid"]
                self.badnet = bssid
                self.smash_counter = 0
            if net_info is None:
                sleep(10)
                continue
            internet_accessible = self.check_internet()
            if not internet_accessible:
                smashed = self.smash(net_info)
                if not smashed:
                    self.smash_counter += 1
                else:
                    print("Seems like we smashed the net!")
            else:
                #Everything seems alright!
                print("Successful connection!")
                
    def stop(self):
        self.smashing = False


if __name__ == "__main__":
    smasher = PortalSmash()
    smasher.run()



