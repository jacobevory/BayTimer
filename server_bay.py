#!/usr/bin/env python
import pika
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QLabel, QLCDNumber, QFormLayout
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
import time
import json


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
		send(j['Bay'], j['isCar'])

		
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
	
		bay1 = QLabel('Bay 1')
		bay2 = QLabel('Bay 2')
		bay3 = QLabel('Bay 3')
		bay4 = QLabel('Bay 4')
		
		lcd1 = QLCDNumber(self)
		lcd2 = QLCDNumber(self)
		lcd3 = QLCDNumber(self)
		lcd4 = QLCDNumber(self)
		
		
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
		grid.addWidget(lcd1, 2, 0)
		
		grid.addWidget(bay3, 3, 0)
		bay3.setAlignment(Qt.AlignCenter)
		bay3.setFont(QtGui.QFont('Calabri', 72))
		grid.addWidget(lcd3, 4, 0)
		
		grid.addWidget(bay2, 1, 1)
		bay2.setAlignment(Qt.AlignCenter)
		bay2.setFont(QtGui.QFont('Calabri', 72))
		grid.addWidget(lcd2, 2, 1)
		
		grid.addWidget(bay4, 3, 1)
		bay4.setAlignment(Qt.AlignCenter)
		bay4.setFont(QtGui.QFont('Calabri', 72))
		grid.addWidget(lcd4, 4, 1)
		
		self.setLayout(grid)
		self.setGeometry(0, 0, width, height)
		
		self.setWindowTitle('Bay Timer')
		self.setWindowState(QtCore.Qt.WindowMaximized)
		self.show()
		
		'''
		timer1 = QtCore.QTimer(self)
		timer2 = QtCore.QTimer(self)
		timer3 = QtCore.QTimer(self)
		timer4 = QtCore.QTimer(self)
		timer1.timeout.connect(self.Time)
		timer2.timeout.connect(self.Time)
		timer3.timeout.connect(self.Time)
		timer4.timeout.connect(self.Time)
		timeoutV = 10
		timer1.start(timeoutV)
		timer2.start(timeoutV)
		timer3.start(timeoutV)
		timer4.start(timeoutV)
		'''
		
		#self.lcd1.resize(250,100)
		
	def startReceiveThread(self):
		print("instantiating")
		self.receive_thread = receiveThread()
		print("Connecting")
		self.receive_thread.update_signal.connect(self.update)
		print("Starting Thread")
		self.receive_thread.start()
		
		
	def update(self, bay, occupancy):
		
		print("Update Received")
		
		
		

if __name__ == "__main__":
	app = QApplication(sys.argv)
	screen_resolution = app.desktop().screenGeometry()
	width, height = screen_resolution.width(), screen_resolution.height()
	app.setApplicationName('Bay Timer')
	main = MainWindow()
	#main.show()
	sys.exit(app.exec_())