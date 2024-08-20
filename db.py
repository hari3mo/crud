import mysql.connector

mydb = mysql.connector.connect(
    host = 'erpcrmdb.cfg0ok8iismy.us-west-1.rds.amazonaws.com',
    user = 'erpcrm', 
    passwd = 'Erpcrmpass1!',
    database = 'erpcrmdb'
)

cursor = mydb.cursor()

cursor.execute('SELECT * FROM Accounts')

accounts = cursor.fetchall()


