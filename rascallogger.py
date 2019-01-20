import sqlite3
from dnslib import DNSRecord,DNSError,QTYPE,RCODE,RR
from datetime import datetime
from dnslib.server import DNSLogger, TCPServer, UDPServer
import logging

try:
    import socketserver
except ImportError:
    import SocketServer as socketserver

logging.basicConfig(filename='example.log',level=logging.DEBUG)

class SQLiteModel:
    def __init__(self, database):
	self.database = database
	self.table = "queries"

        
    def insert(self, data):
	logging.debug("Inser method called with data: %s", " ".join(data))
        self.conn = sqlite3.connect(self.database)
	c = self.conn.cursor()
        c.execute("INSERT INTO " + self.table + " VALUES(?,?,?,?,?,?)",data)
	self.conn.commit()
	self.conn.close()
   

class bribonlogger(DNSLogger):

    def __init__(self,log,prefix, domain, database):
	DNSLogger.__init__(self, log, prefix)
	self.domain = domain
	self.db = SQLiteModel(database)

    def log_request(self,handler,request):
        DNSLogger.log_request(self,handler,request)
	qname=request.q.qname
        now_str = datetime.now().strftime('%Y-%m-%d %H%M%S')
	if self.domain in str(qname):
	    clientip = handler.client_address[0]
            subqname = str(qname).replace("." + self.domain + ".", "")
            domainArr = subqname.split(".")
            if len(domainArr) is 3:
                encoded = domainArr[0]
		try:
                    data = encoded.decode('hex')
                except Exception, e:
                    data = "enc-" + encoded
                part = domainArr[1]
                session = domainArr[2]
                logging.info("DATA -> %s[%s].%s: %s\n" % (clientip, session, part, data,))
		dataArr = [now_str, data, part, session, clientip, self.domain]
		self.db.insert(dataArr)
	    else:
		session = domainArr[-1]
		dataArr = [now_str, subqname, 0, 0, clientip, self.domain]
		self.db.insert(dataArr)
