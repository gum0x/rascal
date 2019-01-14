import sqlite3

conn = sqlite3.connect('bribon.db')

iq = 'insert or replace into output select timestamp, ip, session,  group_concat(query,"") from (select min(date) as timestamp, ip,  session,part, query from queries group by session, part order by session, part) group by session order by session, part;'
conn.execute(iq)
q="select * from output order by timestamp"
result=conn.execute(q)
for row in result:
	print row

conn.close()
	
