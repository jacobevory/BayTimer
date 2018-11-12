#!/usr/bin/env python
import pika
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QLabel, QLCDNumber, QFormLayout
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
import time
import json

timer = [0 for x in range(5)]
s = [0 for x in range(5)]
m = [0 for x in range(5)]
h = [0 for x in range(5)]

isCarLast = [False for x in range(5)]
isCarCurrent = [False for x in range(5)]

credentials = pika.PlainCredentials('bay', 'timer')
parameters = pika.ConnectionParameters(host='localhost', credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue='timer_data', arguments={'x-message-ttl' : 1000})

class receiveThread(QtCore.QThread):

	update_signal = pyqtSignal(int, int)
	
	def __init__(self, parent=None):
		super(receiveThread, self).__init__(parent)		
		
	def send(self, bayPos):
		stop = 0
		reset = 1
		if isCarLast[bayPos] == "True" and isCarCurrent[bayPos] == "False":
			self.update_signal.emit(bayPos, stop)
		elif isCarLast[bayPos] == "False" and isCarCurrent[bayPos] == "True":
			self.update_signal.emit(bayPos, reset)
		elif isCarLast[bayPos] == "False" and isCarCurrent[bayPos] == "False":
			self.update_signal.emit(bayPos, stop)
		else:
			return	
		#self.update_signal.emit(bay, command)

	def callback(self, ch, method, properties, body):
		global isCarLast
		global isCarCurrent
		data_in = body.decode()
		print(" [x] Received %r" % data_in)
		j = json.loads(data_in)
		isCarLast[int(j['Bay'])] = isCarCurrent[int(j['Bay'])]		
		isCarCurrent[int(j['Bay'])] = str(j['isCar'])
		self.send(int(j['Bay']))
		
	def run(self):
	
		channel.basic_consume(self.callback,
						  queue='timer_data',
						  no_ack=True)
		print(' [*] Waiting for messages. To exit press CTRL+C')
		channel.start_consuming()


class MainWindow(QWidget):
	
	
	def __init__(self):
		print("Starting Main Window")
		super(MainWindow, self).__init__()
		self.initUI()
		print("UI Done")
		#self.update_signal.connect(self.update)
		self.startReceiveThread()

	def initUI(self):
		global width
		global height
		global timer
		global s, m, h
	
		#bay1 = QLabel('Bay 1')
		#bay2 = QLabel('Bay 2')
		#bay3 = QLabel('Bay 3')
		#bay4 = QLabel('Bay 4')
		self.lcd = [0 for x in range(5)]
		self.lcd[1] = QLCDNumber(self)
		self.lcd[2] = QLCDNumber(self)
		self.lcd[3] = QLCDNumber(self)
		self.lcd[4] = QLCDNumber(self)		
		
		grid = QGridLayout()
		
		'''
		
		grid.addRow(bay1, bay2)
		grid.addRow(lcd1, lcd2)
		grid.addRow(bay3, bay4)
		grid.addRow(lcd3, lcd4)
		
		'''
		
		#grid.addWidget(bay1, 1, 0)
		#bay1.setAlignment(Qt.AlignCenter)
		#bay1.setFont(QtGui.QFont('Calabri', 72))
		grid.addWidget(self.lcd[1], 0, 0)
		
		#grid.addWidget(bay3, 3, 0)
		#bay3.setAlignment(Qt.AlignCenter)
		#bay3.setFont(QtGui.QFont('Calabri', 72))
		grid.addWidget(self.lcd[3], 2, 0)
		
		#grid.addWidget(bay2, 1, 1)
		#bay2.setAlignment(Qt.AlignCenter)
		#bay2.setFont(QtGui.QFont('Calabri', 72))
		grid.addWidget(self.lcd[2], 1, 0)
		
		#grid.addWidget(bay4, 3, 1)
		#bay4.setAlignment(Qt.AlignCenter)
		#bay4.setFont(QtGui.QFont('Calabri', 72))
		grid.addWidget(self.lcd[4], 3, 0)
		
		self.setLayout(grid)
		self.setGeometry(0, 0, width, height)
		
		self.setWindowTitle('Bay Timer')
		self.setWindowState(QtCore.Qt.WindowMaximized)
		self.show()
		
		
		timer[1] = QtCore.QTimer(self)
		timer[2] = QtCore.QTimer(self)
		timer[3] = QtCore.QTimer(self)
		timer[4] = QtCore.QTimer(self)
		timer[1].timeout.connect(lambda: self.Time(1))
		timer[2].timeout.connect(lambda: self.Time(2))
		timer[3].timeout.connect(lambda: self.Time(3))
		timer[4].timeout.connect(lambda: self.Time(4))
		timeoutV = 1000
		#timer[1].start(timeoutV)
		#timer[2].start(timeoutV)
		#timer[3].start(timeoutV)
		#timer[4].start(timeoutV)
		#self.lcd1.resize(250,100)
	
	
	def Time(self, timernum):
		global s, m, h
		if s[timernum] < 59:
			s[timernum] += 1
		else:
			if m[timernum] < 59:
				s[timernum] = 0
				m[timernum] += 1
			elif m[timernum] == 59 and h[timernum] < 100:
				h[timernum] += 1
				m[timernum] = 0
				s[timernum] = 0
			else:
				self.timer[timernum].stop()
 
		time = self.getStr(h[timernum]) + ":" + self.getStr(m[timernum]) + ':' + self.getStr(s[timernum])
 
		self.lcd[timernum].setDigitCount(len(time))
		self.lcd[timernum].display(time)
	
	def getStr(self, number):
		if number < 10 and number > -1:
			returnStr = '0' + str(number)
		else:
			returnStr = str(number)
		return returnStr
	
	def startReceiveThread(self):
		print("instantiating")
		self.receive_thread = receiveThread()
		print("Connecting")
		self.receive_thread.update_signal.connect(self.update)
		print("Starting Thread")
		self.receive_thread.start()
		
		
	def update(self, pos, com):
		if com == 0:
			timer[pos].stop()
		elif com == 1:
				s[pos] = 0
				m[pos] = 0
				h[pos] = 0
				timer[pos].start(1000)
		else:
			return	
		

if __name__ == "__main__":
	app = QApplication(sys.argv)
	screen_resolution = app.desktop().screenGeometry()
	width, height = screen_resolution.width(), screen_resolution.height()
	app.setApplicationName('Bay Timer')
	main = MainWindow()
	#main.show()
	sys.exit(app.exec_())
