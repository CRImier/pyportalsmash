import requests
import atexit
from time import sleep

from lxml import html

import wpa_cli

class PortalSmash():
    smashing = False
    smash_counter = 0

    badnets_file = "badnets.log"
    badnets = []
    badnet = None

    def __init__(self):
        self.read_badnets()
        atexit.register(self.write_badnets)

    def read_badnets(self):
        with open(self.badnets_file, 'r') as f:
            self.badnets = [line.strip() for line in f.readlines()]

    def write_badnets(self):
        with open(self.badnets_file, 'w') as f:
            f.write('\n'.join(self.badnets))

    def check_internet(self, page="http://www.apple.com/library/test/success.html"):
        try:
            r = requests.get(page)
        except Exception as e:
            print( "Requests exception: {}".format(repr(e)) )
            return None
        else:
            return r.text.lower() == "<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>".lower()
    
    def check_connect_wifi(self):
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

    def smash(self, net_info, url="http://www.google.lv"):
        print("Gotta smash that {}!".format(net_info))
        print("Going to {}!".format(url))
        page = requests.get(url)
        print(page.history)
        tree = html.fromstring(page.text)
        forms = tree.xpath("//li/text()")
        if forms:
            for form in forms: print(repr(form))
            return False
        else:
            #Searching for refresh tags with destination
            meta_tags = tree.xpath("/html/head/meta/")
            for meta_tag in meta_tags: print(repr(meta_tag))
            destination = None
            for tag in meta_tags:
                print(tag.keys())
                for key in tag.keys():
                    print("{} - {}".format(repr(key), repr(tag.get(key))))
                    #Registry-independent fuckery
                    if key.lower() == "http-equiv" and tag.get(key) == "refresh":
                        #Is a refresh tag, getting attribute
                        content_keys = [key for key in tag.keys() if key.lower() == "content"]
                        if not content_keys: print("Content not found!"); continue
                        print(content_keys)
                        content = tag.get(content_keys[0])
                        print(content)
                        if ";" in content:
                            delay, destination = content.split(";")
                        else:
                            delay = content
                            destination = None
                        #Delay attr validation
                        try:
                            delay = int(delay)
                        except ValueError:
                            print("Invalid delay!")
                            delay = 0
                        else:
                            #Boundary checks
                            if delay < 0: delay = 0
                            if delay > 10: delay = 10
                        print("Sleeping for {}".format(delay))
                        sleep(delay)
                        if destination is not None:
                            #Need to go deeper
                            return self.smash(net_info, url=destination)
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
    print("Main, running")
    smasher = PortalSmash()
    smasher.loop()
