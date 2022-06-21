import mysql.connector

def get_connection() :
    connection = mysql.connector.connect(
        host = 'jhdb.ct294vqgyq74.ap-northeast-2.rds.amazonaws.com',
        database = 'memo_db',
        user = 'memo_user',
        password = 'memo1234'
    )
    return connection