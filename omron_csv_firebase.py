import sys
import csv
from datetime import datetime
import pyrebase

config = {
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "storageBucket": ""
}
email = ''
password = ''

arguments = sys.argv

if len(arguments) == 1:
  print ("Usage: python omron_csv_firebase.py CSV_FILE")
  sys.exit()

csvfile = arguments[1]

def main():
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password(email, password)

    ##  CSV_FILE format
    ##  Time,Gateway,Address,Type,RSSI (dBm),Distance (m),Sequence No.,Battery (mV),Temperature (degC),Humidity (%%RH),Light (lx),UV Index,Pressure (hPa),Noise (dB),Discomfort Index,Heat Stroke Risk,Accel.X (mg),Accel.Y (mg),Accel.Z (mg)
    ##  2018-09-17 00:04:53.831591,raspberrypi,FFA511nnnnnn,EP,-66,1.77188476275,69,2830.0,22.68,82.6,0,0.01,996.3,34.64,71.4,23.37,0.0,0.0,0.0

    f = open(csvfile, 'r')
    reader = csv.reader(f)

    for row in reader:
      if row[0] == 'Time':
        continue
      dt = datetime.strptime(row[0][0:19], '%Y-%m-%d %H:%M:%S')
      dt_s = dt.strftime('%s') + row[0][20:23]

      data = {
        "timestamp": int(dt_s),
        "value": {
          "created": int(dt_s),
          "address": row[2],
          "rssi": float(row[4]),
          "distance": float(row[5]),
          "battery": float(row[7]),
          "temperature": float(row[8]),
          "humidity": float(row[9]),
          "light": float(row[10]),
          "uv": float(row[11]),
          "pressure": float(row[12]),
          "noise": float(row[13]),
          "di": float(row[14]),
          "heat": float(row[15])
        }
      }
##      print (data)
      results = db.child("omron").child(row[2]).push(data, user['idToken'])

    f.close()
    return
 
if __name__ == "__main__":
    main()

