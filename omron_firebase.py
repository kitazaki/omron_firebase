# -*- coding: utf-8 -*-
#

from bluepy.btle import Peripheral, DefaultDelegate, Scanner, BTLEException, UUID
import bluepy.btle
import sys
import struct
from datetime import datetime
import argparse
import pyrebase

config = {
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "storageBucket": ""
}
email = ''
password = ''
companyID = 'd502'  # OMRON company ID (Bluetooth SIG.)
address = 'FFA511nnnnnn'  # BT ADDRESS (replace nnnnnn to own device)

Debugging = False
def DBG(*args):
    if Debugging:
        msg = " ".join([str(a) for a in args])
        print(msg)
        sys.stdout.flush()

Verbose = True
def MSG(*args):
    if Verbose:
        msg = " ".join([str(a) for a in args])
        print(msg)
        sys.stdout.flush()

def send2firebase(dataRow):
    (temp, humid, light, uv, press, noise, accelX, accelY, accelZ, batt) = struct.unpack('<hhhhhhhhhB', bytes.fromhex(dataRow))
    MSG(temp/100, humid/100, light, uv/100, press/10, noise/100, (batt+100)/100)

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password(email, password)

    now = datetime.now()
    dt_s = now.strftime("%s") + str(int(now.microsecond/1000))
    data = {
        "timestamp": int(dt_s),
        "value": {
          "created": int(dt_s),
          "address": address,
          "battery": float((batt+100)/100),
          "temperature": float(temp/100),
          "humidity": float(humid/100),
          "light": float(light),
          "uv": float(uv/100),
          "pressure": float(press/10),
          "noise": float(noise/100)
        }
    }
    MSG(data)
    results = db.child("omron").child(address).push(data, user['idToken'])

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.lastseq = None
        self.lasttime = datetime.fromtimestamp(0)

    def handleDiscovery(self, dev, isNewDev, isNewData):
            if isNewDev or isNewData:
                for (adtype, desc, value) in dev.getScanData():
                    if desc == 'Manufacturer' and value[0:4] == companyID:
                        delta = datetime.now() - self.lasttime
                        if value[4:6] != self.lastseq and delta.total_seconds() > 11:
                            self.lastseq = value[4:6]
                            self.lasttime = datetime.now()
                            send2firebase(value[6:])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d',action='store_true', help='debug msg on')

    args = parser.parse_args(sys.argv[1:])

    global Debugging
    Debugging = args.d
    bluepy.btle.Debugging = args.d

    scanner = Scanner().withDelegate(ScanDelegate())
    while True:
        try:
            scanner.scan(5.0)
        except BTLEException:
            MSG('BTLE Exception while scannning.')

if __name__ == "__main__":
    main()

