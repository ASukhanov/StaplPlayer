#!/usr/bin/python

#usage: ./dump_udp_broadcast [-w] [-d[]

data_directory = "/tmp/"
port = 1792  # where do you expect to get a msg?
bufferSize = 7000 # whatever you need

import select, socket
import time
import datetime
import sys, getopt
import struct

ev_offset = 0
ev_hdr = []
sfil = None
run_started = -1
bytesin = 0.
rc = 0
writing_enabled = False
dump_enabled = False
dump_trailer = True

# hex dump
#FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
def dump(src, length=16):
	N=0; result=''
	while src:
		s,src = src[:length],src[length:]
		hexa = ' '.join(["%02X"%ord(x) for x in s])
		#s = s.translate(FILTER)
		#result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
		result += "%04X   %-*s\n" % (N, length*3, hexa)
		N+=length
	return result

def i16(b0,b1):
	return b0<<8 + b1

def lParity(src):
	# very slow longitudinal parity calculator
	#ii = 16
	lpar = 0
	while src:
		wrd = struct.unpack_from('>H',src[:2])
		src = src[2:]
		lpar ^= wrd[0]
		#if ii:
		#	print(hex(lpar))
		#	ii -=1	
	return lpar

#print(str(sys.argv))
for opt in sys.argv:
	if opt == '-w':
		writing_enabled = True
		print('Writing enabled')
	if opt == '-d':
		dump_enabled = True
		print('Dump enabled')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('<broadcast>', port))
rc =  s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
s.setblocking(0)

while True:
	result = select.select([s],[],[])
	msg = result[0][0].recv(bufferSize)
	msglen = len(msg)
	bytesin += msglen
	if run_started == -1:
		run_started = 0
		print('FEM is alive, msgLen=' + str(msglen))
	if msglen == 44:
		if run_started == 1:
			elapsed_sec = time.time() - start
			print('Run stopped, evLen= ' + str(msglen))
			run_started = 0
			if sfil and not sfil.closed:
				fpos = sfil.tell()
				txtout = 'Closed '+sfil.name+'['+str(fpos)+'] after '+str(round(elapsed_sec,1))+'s'
				print(txtout)
				sfil.close()
		continue
	elif run_started == 0:
		print('Run started, evLen= ' + str(msglen))
		run_started = 1
		bytesin = 0.
		if writing_enabled:
			filename = datetime.datetime.today().strftime("%y%m%d%H%M.dq4")
			sfil = open(data_directory+filename,'wb')
			if not sfil.closed:
				txtout = 'Opened '+sfil.name
				print(txtout)
		start = time.time()
		olddifftime = 0

	# Process event
	if msglen < 100:
		print('ERROR short event '+str(msglen))
		continue
	ev_hdr = struct.unpack_from('>HHHHHHHHHHHH',msg,ev_offset*2)
	for ii in range(12):
		print(hex(ev_hdr[ii]).split('0x')[1].zfill(4)),
	ev_trl = struct.unpack_from('>HHHH',msg[-8:])
	print('...'),
	for ii in range(4):
		print(hex(ev_trl[ii]).split('0x')[1].zfill(4)),
	print(' LPar='+hex(lParity(msg)))
	if dump_enabled:
		print(dump(msg))
	if sfil and not sfil.closed:
		sfil.write(msg)
	difftime = int((time.time() - start))
	if sfil and not sfil.closed:
		bytesout = round(sfil.tell()/1000.,1) 
	else:
		bytesout = 0.
	if difftime/10 != olddifftime/10:
		txtout = str(difftime)+'s: evLen='+str(msglen)+', bytes in: '+str(bytesin) + ', out: '+str(bytesout)+'kB'
		print(txtout)
	olddifftime = difftime
