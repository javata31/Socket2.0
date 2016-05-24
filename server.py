# ******************************************************
# This file implements a server for receving and sending
# files.  The server also sends a list of the files in 
# its directory to the client when they are requested.
# ******************************************************
import socket
import sys
import commands
import os.path

#Receives file from client
def recvAll(sock, numBytes):
	#Buffer for what has been received
	recvBuff = ""

	#Used to check if no data was received
	tempBuff = ""

	#get all data
	while len(recvBuff) < numBytes:
		tempBuff = sock.recv(numBytes)

		#no data was received
		if not tempBuff:
			break

		#add to buffer size
		recvBuff += tempBuff

	return recvBuff

#Sends file to client
def sendFile(cmd, sock):
	#file name identified
	fileName = cmd[1]

	#open file and get contents
	fileObj = open(fileName, "r")

	#contents of the file
	fileData = None

	while True:
		#used to count how much of the data has been sent
		numSent = 0

		#grab the of the file
		fileData = fileObj.read(15000)

		#if not empty
		if fileData:
			#get size of the file
			fileSize = str(len(fileData))

			#Prepend 0's to the size of string
			# to make 10 bytes
			while len(fileSize) < 10:
				fileSize = "0" + fileSize

			#Prepend size of file to fileData
			fileData = fileSize + fileData

			#send file information to client
			while len(fileData) > numSent:
				numSent += dataTransmitter.send(fileData[numSent:])
		else:
			break

	#close the connection used to transfer data
	dataTransmitter.close()


#Throw flag if user does not send two arguments
if len(sys.argv) != 2:
	print "USAGE: python " + sys.argv[0] + " <Server Port>"
	exit()

#Listen port number
listenPort  = int(sys.argv[1])

#Connect to socket
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind to specidied port
connSock.bind(('', listenPort))

#Listen for connections
connSock.listen(1)

#Leave connection open
while True:
	print "\n"
	print "Waiting for connections:"

	#Accept conection
	clientSock, addr = connSock.accept()

	#Print client address
	print "Accepted connection from client: ", addr
	print "\n"

	#Case for second connections
	while True:
		#Take in client's command and ephemeral port number
		cmd = clientSock.recv(1024)

		#If cmd is blank, jump out of loop
		if (len(cmd) == 0):
			break

		#Parse string to list
		cmd = cmd.split()

		#Client specified "get"
		if(cmd[0] == "get"):
			#local host is the server's address
			serverAddr = "localhost"

			#identify ephermeral port number
			ephemeralPort = int(cmd[2])

			#open temporary connection to socket for data transfer
			dataTransmitter = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			dataTransmitter.connect((serverAddr, ephemeralPort))
		
			#if file exists in directory
			if(os.path.isfile(cmd[1])):
				#send file to client
				sendFile(cmd, dataTransmitter)
				print "'get' Command successfully processed \n"
			#unsuccesful 			
			else:
				dataTransmitter.send("Invalid file name \n")
				print "'get' Command was unsuccessful.  Not real file name. \n"                      

		#Client specified "put"
		if(cmd[0] == "put"):
			#initialize ephemeral port number
			ephemeralPort = int(cmd[2])

			#open connection for data transfer
			dataTransmitter = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			dataTransmitter.connect(("localhost", ephemeralPort))

			#used to get content inside of the file
			fileData = ""

			#get size of the file
			fileSize = 0
	
			try:
				#get length of file
				fileSize = int(recvAll(dataTransmitter, 10))

				#get contents of the file
				fileData = recvAll(dataTransmitter, fileSize)
				
				if(fileData):	
					#open and write the file data
					file = open(cmd[1], "w")
					file.write(fileData)

					#close the file
					file.close()
					print "'put' Command successfully processed \n"
			
			#invalid filename, throw error
			except ValueError:
				print "'put' Command was unsuccessfull. File name may be invalid\n"
				
			#close data temporary transfer connection
			dataTransmitter.close()

		#Client specified "ls"
		if(cmd[0] == "ls"):			
			#initialize ephemeral port number
			ephemeralPort = int(cmd[1])

			#open connection for data transfer
			dataTransmitter = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			dataTransmitter.connect(("localhost", ephemeralPort))
			
			#checks that ls command has nothing after it			
			if(len(cmd) == 2):
				#get list of content in current directory
				for line in commands.getstatusoutput('ls -l'):
					#Only send files if list is not empty					
					if line:				
						dataTransmitter.send(str(line))
			else:
				print "'ls' Command was unsuccessfull.\n"

			#close temporary data transfer connection
			dataTransmitter.close()
			print "'ls' Command successfully processed \n"

	#closed connection
	print "Client closed the connection"


