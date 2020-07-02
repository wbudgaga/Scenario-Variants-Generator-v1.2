import socket
import sys

hostname = socket.gethostname()
d='/s/%s/a/tmp/wbudgaga'%(hostname)
if __name__ == '__main__':
	s   = int(sys.argv[1])
	e   = int(sys.argv[2])
	v='variants_%s_%s.csv'%(s,e)
	fn='%s/%s'%(d,v)
	f=open(fn)
	ls=f.readlines()
	f.close()
	print "%s ==>%s"%(hostname, len(ls))

