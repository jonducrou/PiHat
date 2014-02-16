import traceback
import time
import sys
import socket
from subprocess import Popen,PIPE
from subprocess import call
while True:

	try:
		print "getting ip..."
		ip = socket.gethostbyname("smokinn-lapbeast.local")
		print "found ip: ", ip, " connecting..."
		p1 = Popen(["raspivid","-t","999999","-h","480","-w","720","-fps","30","-o","-"],stdout=PIPE)
		print "finished p1"
		p2 = Popen(["nc",ip,"5001"],stdin=p1.stdout, stdout=PIPE)
		time.sleep(3)
	except:
		print "failed connecting..."
		time.sleep(10)
	try:
		print "start..."
		killFileExists = os.path.exists("~/startup.kill")
		print "checking if killfile exists"
		if killFileExists:
			os.unlink("~/startup.kill")
			sys.exit()
	except:
		print "failed validating kill file"
