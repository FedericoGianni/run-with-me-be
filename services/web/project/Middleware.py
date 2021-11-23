from dbmysql.DbController import DbController



class Middleware():
    def __init__(self) -> None:
        self.dbController = DbController()
        pass

    def register(self, message):
        pass

    def getEvents(self):
        events = self.dbController.getEvents()