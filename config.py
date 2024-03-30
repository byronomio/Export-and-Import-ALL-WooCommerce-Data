import pymysql

# config.py

#Variables
TABLE_PREFIX = ''
DUMPED_TABLE_PREFIX = ''
TIMESTAMP = ''

#Import from LIVE
DB_NAME = ""
DB_USER = ""
DB_PASSWORD = ""
DB_HOST = ""
DB_CHASRET = ""
DB_UNIX_SOCKET = ""

#Imported from LIVE into LOCAL
LOCAL_DB_HOST = ""
LOCAL_DB_USER = ""
LOCAL_DB_PASSWORD = ""
LOCAL_DB_NAME = ""
LOCAL_CHASRET  = ""
LOCAL_UNIX_SOCKET  = ""

def live_connection():
    return pymysql.connect(host=DB_HOST,
                           user=DB_USER,
                           password=DB_PASSWORD,
                           database=DB_NAME,
                           charset=LOCAL_CHASRET,
                           unix_socket=LOCAL_UNIX_SOCKET,                           
                           cursorclass=pymysql.cursors.DictCursor)

def local_connection():
    return pymysql.connect(host=LOCAL_DB_HOST,
                           user=LOCAL_DB_USER,
                           password=LOCAL_DB_PASSWORD,
                           database=LOCAL_DB_NAME,
                           charset=LOCAL_CHASRET,
                           unix_socket=LOCAL_UNIX_SOCKET,
                           cursorclass=pymysql.cursors.DictCursor)
