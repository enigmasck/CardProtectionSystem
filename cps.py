import datetime
from picamera import PiCamera
from time import sleep
from pip._vendor import requests
from pip._vendor.distlib.compat import raw_input
from random import seed, randint
import serial

camera = PiCamera()
tDate = datetime.datetime.today()
PortRF = serial.Serial('/dev/ttyAMA0', 9600)
store_id = "5e257a59f5de6e730eb85d80"

def readRFID():
    print("Running RFID Reader...")
    ID = ""
    while len(ID) < 12:
        read_byte = PortRF.read()
        if read_byte == "\x02":
            for Counter in range(0, 12):
                read_byte = PortRF.read()
                ID = ID + str(read_byte)

    PortRF.flushInput()
    PortRF.flushOutput()
    return ID

def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial

print("List of commands: (M)ake(P)urchase, (Ex)it, (R)ead(C)ard(N)umber ")

while(True):
    cmd = raw_input("Please enter a command: ")
    if(cmd.lower() == 'mp' or cmd.lower == ("MakePurchase")):
        purAmnt = raw_input("Please enter the purchase amount:")
        camera.start_preview()
        card_id = readRFID()
        #perform check for max attempts before preceding
        pl = {'cardId':card_id}
        try:
            maxRep = requests.get('http://etu-web2.ut-capitole.fr:3013/aws/getMaxAttempts', params=pl)
        except:
            print("There was an error establishing a connection with the server...")

        maxRepJson = maxRep.json()

        if maxRepJson['result'] == "success":
            randNum = randint(100, 10000000000)
            tDateStr = str(tDate.year) + str(tDate.month) + str(tDate.day)
            fileName = str(card_id) + "_" + tDateStr + "_" + str(randNum) +'.jpg'
            fileNamePath = '/home/pi/Pictures/'+ fileName
            #will add custnum and cardnum
            sleep(2)
            camera.capture(fileNamePath)
            camera.stop_preview()
            print("Authenticating...")
            #send photo to server
            multipart_form_data = {
                'file': (fileName, open(fileNamePath, 'rb')),
                'path': (None, '/home/pi/Pictures'),
                'origFileName': (None, fileName),
                'cardId': (None,card_id),
                'storeId': (None,store_id),
                'purAmnt': (None, purAmnt),
                'terminalNum': (None, getserial())
            }

            try:
                response = requests.post('http://etu-web2.ut-capitole.fr:3013/aws/transaction', files=multipart_form_data)
            except:
                print("There was an error establishing a connection with the server...")

            rJson = response.json()
            #print("response json",rJson)

            if(rJson['match'] == "success"):
                print("Your transaction was successful")
            elif(rJson['match'] == "fail"):
                print("Authentication failed.")
            elif(rJson['match'] == "ERROR"):
                print("There was an error processing the transaction")
                print("Error message: %s " % (rJson['value']) )
        else:
            print("There have been too many failed attempts authentication in a 24 hour period.")

        card_id = ""

    elif (cmd.lower() == 'rcn' or cmd.lower() == 'ReadCardNumber'):
        cardNum = readRFID()
        print("Your card number is: %s" % (cardNum))
    elif(cmd.lower() == 'ex' or cmd.lower() == 'exit'):
        break


