# -*- coding: utf-8 -*
import serial
import time
import sys
import pika
from client_config import serverIP, user, password, bayNum, isCar_UpperLimit, isCar_LowerLimit, queueName

ser = serial.Serial('/dev/serial0', 115200)



credentials = pika.PlainCredentials(user, password)
parameters = pika.ConnectionParameters(host=serverIP, credentials=credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()
#channel.queue_declare(queue=queueName, arguments={'x-message-ttl' : 1000})


roll1 = -1
roll2 = -2
roll3 = -3
round = 1
ready = False
distance = 0
isCar = False


def sendData():
	global distance
	global round
	global roll1
	global roll2
	global roll3
	global ready
	global isCar
	global bayNum
	
	sendBody = "{\"Bay\":\"" + str(1) + "\", \"isCar\":\"" + str('True') + "\"}"
	
	channel.basic_publish(exchange='',
				  routing_key=queueName,
				  body=sendBody)
	print(sendBody)
		
		
	

if __name__ == '__main__':
	   try:
			 while True:
				    if ser.is_open == False:
						  ser.open()
				    getTFminiData()
				    sendData()
	   except KeyboardInterrupt:   # Ctrl+C
			 if ser != None:
				    ser.close()
			 connection.close()
	   except:
			 if ser != None:
				    ser.close()
			 connection.close()
			 sys.exit()

