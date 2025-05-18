from socket import *
import pickle
from constMP import *
import time
import sys

serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('0.0.0.0', SERVER_PORT))
serverSock.listen(6)

def mainLoop():
	cont = 1
	while 1:
		nMsgs = promptUser()
		if nMsgs == 0:
			break
		clientSock = socket(AF_INET, SOCK_STREAM)
		clientSock.connect((GROUPMNGR_ADDR,GROUPMNGR_TCP_PORT))
		req = {"op":"list"}
		msg = pickle.dumps(req)
		clientSock.send(msg)
		msg = clientSock.recv(2048)
		clientSock.close()
		peerList = pickle.loads(msg)
		print("List of Peers: ", peerList)
		startPeers(peerList,nMsgs)
		print('Now, wait for the message logs from the communicating peers...')
		waitForLogsAndCompare(nMsgs)
	serverSock.close()

def promptUser():
	nMsgs = int(input('Enter the number of messages for each peer to send (0 to terminate)=> '))
	return nMsgs

def startPeers(peerList,nMsgs):
	# Connect to each of the peers and send the 'initiate' signal:
	peerNumber = 0
	for peer in peerList:
		clientSock = socket(AF_INET, SOCK_STREAM)
		clientSock.connect((peer, PEER_TCP_PORT))
		msg = (peerNumber,nMsgs)
		msgPack = pickle.dumps(msg)
		clientSock.send(msgPack)
		msgPack = clientSock.recv(512)
		print(pickle.loads(msgPack))
		clientSock.close()
		peerNumber = peerNumber + 1

def waitForLogsAndCompare(N_MSGS):
	# Loop to wait for the message logs for comparison:
	numPeers = 0
	msgs = [] # each msg is a list of tuples (with the original messages received by the peer processes)

	# Receive the logs of messages from the peer processes
	while numPeers < N:
		(conn, addr) = serverSock.accept()
		msgPack = conn.recv(32768)
		print ('Received log from peer')
		conn.close()
		msgs.append(pickle.loads(msgPack))
		numPeers = numPeers + 1

	unordered = 0

	# Compare the lists of messages
	for j in range(0,N_MSGS-1):
		firstMsg = msgs[0][j]
		for i in range(1,N-1):
			if firstMsg != msgs[i][j]:
				unordered = unordered + 1
				break
	
	print ('Found ' + str(unordered) + ' unordered message rounds')


# Initiate server:
mainLoop()
