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
    return ID


print("List of commands: (R)ead(Ca)rd, (Ex)it ")


while(True):
    cmd = raw_input("Please enter a command: ")
    if(cmd.lower() == 'rca' or cmd.lower == ("ReadCard")):
        camera.start_preview()
        card_id = readRFID()
        print("card_id=", card_id)
        randNum = randint(100, 10000000000)
        tDateStr = str(tDate.year) + str(tDate.month) + str(tDate.day)
        fileName = str(card_id) + "_" + tDateStr + "_" + str(randNum) +'.jpg'
        fileNamePath = '/home/pi/Pictures/'+ fileName
        #will add custnum and cardnum
        camera.capture(fileNamePath)
        camera.stop_preview()
        print("Authenticating...")
        print('filename=',fileName)
        #send photo to server
        multipart_form_data = {
            'file': (fileName, open(fileNamePath, 'rb')),
            'path': (None, '/home/pi/Pictures'),
            'origFileName': (None, fileName),
            'cardId': (None,card_id),
            'storeId': (None,store_id)
        }

        response = requests.post('http://etu-web2.ut-capitole.fr:3013/aws/transaction', files=multipart_form_data)

        print(response.content)
        card_id = ""

    elif(cmd.lower() == 'ex' or cmd.lower() == 'exit'):
        break
