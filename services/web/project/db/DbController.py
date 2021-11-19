from sqlalchemy import create_engine


class DbController():

    def __init__(self):
        self.__engine = create_engine('postgresql://postgress:postgress@db:5432/postgress')
