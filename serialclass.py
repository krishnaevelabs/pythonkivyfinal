import serial
import serial.tools.list_ports
import csv
import os
from messagecontroller import nurseMessageParser as msgParser

from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel


class serialClass:
    vendorId = ""
    processId = ""
    device = ""
    fileData = []

    def __init__(self):
        print('created')

    def ports(self):
        ports = list(serial.tools.list_ports.comports())
        print(ports)
        for port in ports:
            if port.vid == 4292 and port.pid == 60000 or port.vid == 1240 and port.pid == 61336:
                self.vendorId = port.vid
                self.processId = port.pid
                self.device = port.device
                print(port.device)

    def readIncomingMessage(self, buttons, queue, test1):
        print("in serial")
        buttons = buttons
        #print(buttons)
        while True:
            try:
                arduino = serial.Serial('/dev/ttyUSB0', 9600)
                test1.update_conn_status("Connected")
                arduino.bytesize = 8
                arduino.timeout = 1
                value = str(arduino.readline())  # .decode("utf-8"))
                value = value[2: -1]
                if value:
                    #print(value)
                    messageData = msgParser(value)
                    if messageData is not None:
                        if messageData[2] == '0':
                            bob = buttons.get(messageData[0])
                            arduino.write(f'{bob.id}-0-{bob.sendAck}'.encode())
                            #print(f'{bob.id}-0-{bob.sendAck} sent')
                            queue.append(messageData)
                        else:
                            bob = buttons.get(messageData[0])
                            arduino.write(f'{bob.id}-0-ack'.encode())
                            #print(f'{bob.id}-0-ack sent')
                            queue.append(messageData)

            except:
                test1.update_conn_status("Connection Error")
                arduino.close()
        #return messageData


    def readcsv(self):
        with open(os.getcwd() + '/carecalldata.csv', 'rt')as f:
            file = csv.reader(f)
            for row in file:
                self.fileData.append(row)
        return self.fileData

    def write_data(self, item):
        arduino = serial.Serial('/dev/ttyUSB0', 9600)
        arduino.write(item.encode())
        #print(f"{item} sent")
