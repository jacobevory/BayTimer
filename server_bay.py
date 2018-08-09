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
channel.queue_declare(queue='timer_data')

class receiveThread(QtCore.QThread):

	update_signal = pyqtSignal(str, str)
	
	def __init__(self, parent=None):
		super(receiveThread, self).__init__(parent)		
		
	def send(bay, occupancy):
		self.update_signal.emit(bay, occupancy)

	def callback(ch, method, properties, body):
		data_in = body.decode("ascii")
		print(" [x] Received %r" % data_in)
		j = json.loads(data_in)
		isCar[j['Bay']] = j['isCar']

		
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
		self.startReceiveThread()

	def initUI(self):
		global width
		global height
		global timer
		global s, m, h
	
		bay1 = QLabel('Bay 1')
		bay2 = QLabel('Bay 2')
		bay3 = QLabel('Bay 3')
		bay4 = QLabel('Bay 4')
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
		
		grid.addWidget(bay1, 1, 0)
		bay1.setAlignment(Qt.AlignCenter)
		bay1.setFont(QtGui.QFont('Calabri', 72))
		grid.addWidget(self.lcd[1], 2, 0)
		
		grid.addWidget(bay3, 3, 0)
		bay3.setAlignment(Qt.AlignCenter)
		bay3.setFont(QtGui.QFont('Calabri', 72))
		grid.addWidget(self.lcd[3], 4, 0)
		
		grid.addWidget(bay2, 1, 1)
		bay2.setAlignment(Qt.AlignCenter)
		bay2.setFont(QtGui.QFont('Calabri', 72))
		grid.addWidget(self.lcd[2], 2, 1)
		
		grid.addWidget(bay4, 3, 1)
		bay4.setAlignment(Qt.AlignCenter)
		bay4.setFont(QtGui.QFont('Calabri', 72))
		grid.addWidget(self.lcd[4], 4, 1)
		
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
		timer[1].start(timeoutV)
		#timer[2].start(timeoutV)
		#timer[3].start(timeoutV)
		#timer[4].start(timeoutV)
		#self.lcd1.resize(250,100)
	
	
	def Time(self, timernum):
		global s, m, h
		if s[timernum] < 10:
			s[timernum] += 1
		else:
			if m[timernum] < 10:
				s[timernum] = 0
				m[timernum] += 1
			elif m[timernum] == 10 and h[timernum] < 24:
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
		
		
	def run(self):
		
		for bayPos in range(1,4):
			if isCarLast[bayPos] == True and isCarCurrently[bayPos] == False:
				timer[bayPos].stop()
			elif isCarLast[bayPos] == False and isCarCurrently[bayPos] == True:
				timer[bayPos].reset()
				timer[bayPos].start(1000)
			elif isCarLast[bayPos] == False and isCarCurrently[bayPos] == False:
				timer[bayPos].stop()
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