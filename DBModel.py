from peewee import *

db = MySQLDatabase("Bug_Clustering", user='root', passwd='mpcrrover')


class TicketDBModel(Model):
    description = TextField()
    classification = CharField()
    system = CharField()

    @classmethod
    def select_by_system(cls, system_name):
        if not cls.table_exists():
            return
        return cls.select().where(cls.system == system_name)

    @classmethod
    def overwrite_system_rows(cls, system_name, list_of_dicts):
        if not cls.table_exists():
            cls.create_table()

        cls.reset_system_rows(system_name)
        cls.insert_atomically(list_of_dicts)

    @classmethod
    def reset_system_rows(cls, system_name):
        if not cls.table_exists():
            return
        cls.delete().where(cls.system == system_name).execute()

    @classmethod
    def insert_atomically(cls, list_of_dicts):
        if not cls.table_exists():
            cls.create_table()

        with db.atomic():
            cls.insert_many(list_of_dicts).execute()

    @classmethod
    def random(cls, system_name):
        if not cls.table_exists():
            return

        return cls.select_by_system(system_name).order_by(fn.Rand())

    class Meta:
        database = db


class Full_PreProcessed_Keyword(TicketDBModel):
    pass


class Terse_PreProcessed_Keyword(TicketDBModel):
    pass


class Stemmed_Keyword(TicketDBModel):
    pass


class LFF_Keywords(TicketDBModel):
    pass