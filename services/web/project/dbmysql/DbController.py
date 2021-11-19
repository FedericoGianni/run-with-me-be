from sqlalchemy import create_engine
DB_TYPE = 'mysql'
DB_USER = 'hello_flask'
DB_PASSWORD = 'hello_flask'
DB_ADDRESS = 'db:3306'
DB_NAME = 'hello_flask_prod'

class DbController():

    
    def __init__(self):
        self.__engine = create_engine(DB_TYPE+"://"+DB_USER+":"+DB_PASSWORD+"@"+DB_ADDRESS+"/"+DB_NAME, pool_pre_ping=True)