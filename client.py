import socket
import os
import sys
import commands

#Receives file from server
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

#Sends file to server
def sendFile(cmd, sock):
	#file name identified
	fileName = cmd[1]

	try:
		#open file and get contents
		fileObj = open(fileName, "r")
	
		#contents of the file
		fileData = None

		while True:

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
	
				#used to count how much of the data has been sent
				numSent = 0
	
				#send file information to client
				while len(fileData) > numSent:
					numSent += serverSocket.send(fileData[numSent:])
			else:
				break
	
		fileSize = numSent-10
	
		#Output the name and the size of the file sent to server
		print "The size of the file sent is: " + str(fileSize) + " bytes"
		print "The file sent was: " + fileName
		print "\n"

		#close the connection used to transfer data
		serverSocket.close()

	#file name was invalid	
	except:
		print "Invalid file name \n"				


#Throw flag if user did not supply enough arguments
if (len(sys.argv) < 2):
	print "Usage python " + sys.argv[0] + "<FILE NAME>"

#Server addres
serverAddr = sys.argv[1]

#Server port
serverPort = sys.argv[2]

#Create a TCP Socket
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect to the server
connSock.connect((serverAddr, int(serverPort)))

#Welcome message
print "\n"
print "Welcome!"
print "Use commands: ls, get <FILE NAME>, put <FILE NAME>, or quit"
print "\n"

#grab input for ftp communication
cmd = raw_input("<ftp> ")

#sanitate user's commands
while True:
	if cmd:
		#separate input by spaces
		cmd = cmd.split()
		
		#get, put, ls, lls or quit commands needed for ftp communication between server and client
		if(cmd[0] == "get" or cmd[0] == "put" or cmd[0] == "ls" or cmd[0] == "lls" or cmd[0] == "quit"):

			#validate get command's format
			if(cmd[0] == "get"):
				if(len(cmd) == 2):			
					break
				else:
					print "Must include <FILE NAME>"
					cmd = raw_input("<ftp> ")
								
			#vaidate put command's format
			if(cmd[0] == "put"):
				if(len(cmd) == 2):
					break
				else:
					print "Must include <FILE NAME>"
					cmd = raw_input("<ftp> ")
			
			#vaidate ls command's format
			if(cmd[0] == "ls"):
				if(len(cmd) == 1):
					break
				else:
					print "did you means ls?"
					cmd = raw_input("<ftp> ")
			
			#vaidate lls command's format	
			if(cmd[0] == "lls"):
				if(len(cmd) == 1):
					break
				else:
					print "did you means lls?"			
					cmd = raw_input("<ftp> ")
				
			#validate quit command
			if(cmd[0] == "quit"):
				if(len(cmd) == 1):
					break
				else:
					print "did you mean quit?"
					cmd = raw_input("<ftp> ")

		#command does not exist
		else:
			print "Invalid command.  Use commands: ls, get <FILE NAME>, put <FILE NAME>, or quit"
			cmd = raw_input("<ftp> ")	
	
	#cmd was empty.  input cmd	
	else:
		print "Invalid command.  Use commands: ls, get <FILE NAME>, put <FILE NAME>, or quit"	
		cmd = raw_input("<ftp> ")

#handle user's commands
while (cmd[0] == "get" or cmd[0] == "put" or cmd[0] == "ls" or cmd[0] == "lls"):
	
	#connect to server for any command except ls
	if(cmd[0] != "lls"):
	
		#open temporary data transfer connection
		cmdSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Bind the socket to port 0
		cmdSocket.bind(('',0))

		# Retreive the ephemeral port number
		ephemeralPort = cmdSocket.getsockname()[1]
		
		#client requested get
		if(cmd[0] == "get"):
			#Concatenate user command with ephemeral port number
			cmdData = cmd[0] + " " + cmd[1] + " " + str(ephemeralPort)
	
			#Send that information to server through current connection
			connSock.send(cmdData)
	
			#listen for server's response
			cmdSocket.listen(1)
	
			#accept the connection
			serverSocket, addr = cmdSocket.accept()
			print "Data transfer channel connection established. \n"
	
			#used to get content inside of the file
			fileData = ""
	
			#get and print size of the file
			fileSize = 0

			try:
				#grab length of file
				fileSize = int(recvAll(serverSocket, 10))
				print "The size of the received file is: " + str(fileSize) + " bytes"
	
				#get contents of the file
				fileData = recvAll(serverSocket, fileSize)
		
				#print name of the file
				print "The name of the received file is: " + cmd[1]
				print "\n"
		
				#open and write the file data
				file = open(cmd[1], "w")
				file.write(fileData)
	
				#close the file
				file.close()

			#error handeler for invalid name	
			except ValueError:
				print "Invalid file name \n"
				serverSocket.close()
				#break				

			#close data temporary transfer connection
			serverSocket.close()

		#client requested put
		elif(cmd[0] == "put"):
			#Concatenate user command with ephemeral port number
			cmdData = cmd[0] + " " + cmd[1] + " " + str(ephemeralPort)
	
			#Send that information to server through current connection
			connSock.send(cmdData)
	
			#listen for server's response
			cmdSocket.listen(1)
	
			#accept the connection
			serverSocket, addr = cmdSocket.accept()
			print "Data transfer channel connection established. \n"
			
			sendFile(cmd, serverSocket)
			serverSocket.close()

		#client requested ls	
		elif(cmd[0] == "ls"):

			#Concatenate user command with ephemeral port number
			cmdData = cmd[0] + " " + str(ephemeralPort)
	
			#Send that information to server through current connection
			connSock.send(cmdData)
	
			#Listen for server's response
			cmdSocket.listen(1)
	
			#Accept connection from server
			serverSocket, addr = cmdSocket.accept()
			print "Data transfer channel connection established. \n"
	
			#Server's response
			cmdResponse = serverSocket.recv(9000)
			print(cmdResponse)
			print "\n"

			#Close temporary data connection
			serverSocket.close()

	#client requested lls
	else:
		#get and print list of content in current directory
		for line in commands.getstatusoutput('ls -l'):
			print(str(line))	

		print"\n"

	#grab input for ftp communication
	cmd = raw_input("<ftp> ")

	#sanitate user's commands
	while True:
		if cmd:
			#separate input by spaces
			cmd = cmd.split()
		
			#get, put, ls, lls or quit commands needed for ftp communication between server and client
			if(cmd[0] == "get" or cmd[0] == "put" or cmd[0] == "ls" or cmd[0] == "lls" or cmd[0] == "quit"):

				#validate get command's format
				if(cmd[0] == "get"):
					if(len(cmd) == 2):			
						break
					else:
						print "Must include <FILE NAME>"
						cmd = raw_input("<ftp> ")
								
				#vaidate put command's format
				if(cmd[0] == "put"):
					if(len(cmd) == 2):
						break
					else:
						print "Must include <FILE NAME>"
						cmd = raw_input("<ftp> ")
			
				#vaidate ls command's format
				if(cmd[0] == "ls"):
					if(len(cmd) == 1):
						break
					else:
						print "did you means ls?"
						cmd = raw_input("<ftp> ")
			
				#vaidate lls command's format	
				if(cmd[0] == "lls"):
					if(len(cmd) == 1):
						break
					else:
						print "did you means lls?"			
						cmd = raw_input("<ftp> ")
					
				#validate quit command
				if(cmd[0] == "quit"):
					if(len(cmd) == 1):
						break
					else:
						print "did you mean quit?"
						cmd = raw_input("<ftp> ")

			#command does not exist
			else:
				print "Invalid command.  Use commands: ls, get <FILE NAME>, put <FILE NAME>, or quit"
				cmd = raw_input("<ftp> ")	
	
		#cmd was empty.  input cmd	
		else:
			print "Invalid command.  Use commands: ls, get <FILE NAME>, put <FILE NAME>, or quit"	
			cmd = raw_input("<ftp> ")
	print "\n"


#close connection
connSock.close()
