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
channel.queue_declare(queue=queueName, arguments={'x-message-ttl' : 1000})

roll1 = -1
roll2 = -2
roll3 = -3
round = 1
ready = False
distance = 0
isCar = False


def getTFminiData():
	global distance
	global ready
	#time.sleep(0.1)
	count = ser.in_waiting
	if count > 8:
		ready = True
		recv = ser.read(9)   
		ser.reset_input_buffer() 
		# type(recv), 'str' in python2(recv[0] = 'Y'), 'bytes' in python3(recv[0] = 89)
		# type(recv[0]), 'str' in python2, 'int' in python3 
		
		if recv[0] == 0x59 and recv[1] == 0x59:	 #python3
			distance = recv[2] + recv[3] * 256
			strength = recv[4] + recv[5] * 256
			print('(', distance, ',', strength, ')')
			ser.reset_input_buffer()
			
		if recv[0] == 'Y' and recv[1] == 'Y':	 #python2
			lowD = int(recv[2].encode('hex'), 16)	  
			highD = int(recv[3].encode('hex'), 16)
			lowS = int(recv[4].encode('hex'), 16)	  
			highS = int(recv[5].encode('hex'), 16)
			distance = lowD + highD * 256
			strength = lowS + highS * 256
			print(distance, strength)
		
		# you can also distinguish python2 and python3: 
		#import sys
		#sys.version[0] == '2'	#True, python2
		#sys.version[0] == '3'	#True, python3

def sendData():
	global distance
	global round
	global roll1
	global roll2
	global roll3
	global ready
	global isCar
	global bayNum
	
	
	if ready:
		ready = False

		if round == 1:
			roll1 = distance
			round = 2
		elif round == 2:
			roll2 = distance
			round = 3
		elif round == 3:
			roll3 = distance
			round = 1
		
		if roll1 == roll2 == roll3:
			roll1 = -1
			roll2 = -2
			roll3 = -3
			if ((distance < isCar_UpperLimit) and (distance > isCar_LowerLimit)) or (distance == 65535):
				isCar = True
			else:
				 isCar = False
			
		sendBody = "{\"Bay\":\"" + str(bayNum) + "\", \"isCar\":\"" + str(isCar) + "\"}"
		
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
