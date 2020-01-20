import datetime
from picamera import PiCamera
from time import sleep
from pip._vendor.distlib.compat import raw_input
from random import seed, randint
from random import random

camera = PiCamera()
seed(167)
tDate = datetime.datetime.today()

print("List of commands: (T)ake(P)hoto, (Ex)it ")


while(True):
    cmd = raw_input("Please enter a command: ")
    if(cmd.lower() == 'tp' or cmd.lower == ("TakePhoto")):
        camera.start_preview()
        sleep(4)
        randNum = randint(100, 10000000000)
        tDateStr = str(tDate.year) +  str(tDate.month) + str(tDate.day)
        fileName = tDateStr + str(randNum)
        #will add custnum and cardnum
        camera.capture('/home/pi/Pictures/'+ fileName +'.jpg')
        camera.stop_preview()
    elif(cmd.lower() == 'ex' or cmd.lower() == 'exit'):
        break
