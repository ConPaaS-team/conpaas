import MySQLdb


db = MySQLdb.connect("localhost","root","ErtPoi")
exc = db.cursor()
exc.execute("show databases;")
ret = exc.fetchall()
for retr in ret: 
    for retrt in retr:
        print retrt
db.close()