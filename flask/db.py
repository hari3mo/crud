import mysql.connector

mydb = mysql.connector.connect(
    host = 'aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com',
    user = 'erpcrm', 
    passwd = 'Erpcrmpass1!',
    database = 'erpcrmdb'
)

cursor = mydb.cursor()

cursor.execute('SELECT * FROM test')

for row in cursor:
    print(row)


