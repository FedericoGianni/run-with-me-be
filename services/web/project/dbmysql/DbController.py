from sqlalchemy import create_engine
from sqlalchemy import create_engine, MetaData, Table, and_

from project.dbmysql.DbParser import DbParser

DB_TYPE = 'mysql+pymysql'
DB_USER = 'hello_flask'
DB_PASSWORD = 'hello_flask'
DB_ADDRESS = 'db:3306'
DB_NAME = 'hello_flask_prod'

class DbController():

    
    def __init__(self):
        self.__engine = create_engine(DB_TYPE+"://"+DB_USER+":"+DB_PASSWORD+"@"+DB_ADDRESS+"/"+DB_NAME, pool_pre_ping=True)
        metadata = MetaData()
        self.__eventsTable = Table("events", metadata, autoload = True, autoload_with = self.__engine)
        self.__parser = DbParser()


    def getEvents(self):
        # sqlalchemy query to db
        pass


    # def geteventsUser(self):
    #     """
    #     A method that returns a list of complete device objects, queried from the database with a specific user permission
    #     :return: the list of complete device object
    #     """

    #     __connection = self.__engine.connect()
    #     try:
    #         query = select([self.__eventsTable]).select_from().where(and_(self.__eventsTable.c.client_uuid == [0], self.__eventsTable.c.is_deleted == False))
    #         result = __connection.execute(query).fetchall()
    #         result = self.__event2Json(result)
    #     except Exception as e:
    #         logging.error("{message}.".format(message=e))
    #         result = False, GenericDatabaseError(e)
    #     __connection.close()
    #     return result




