from peewee import *
#systems = ['cassandra', 'flume', 'hbase', 'hdfs', 'mapreduce', 'zookeeper']

db = MySQLDatabase("Bug_Clustering", user='root', passwd='mpcrrover')


class TicketDBModel(Model):
    description = TextField()
    classification = CharField()
    system = CharField()
    title = TextField()
    status = CharField()
    issue_number = CharField()
    target = CharField()

    @classmethod
    def reset_table(cls):
        if cls.table_exists():
            cls.drop_table()

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
    class cassandra_Full_PreProcess(TicketDBModel):
        pass
    class flume_Full_PreProcess(TicketDBModel):
        pass
    class hbase_Full_PreProcess(TicketDBModel):
        pass
    class hdfs_Full_PreProcess(TicketDBModel):
        pass
    class mapreduce_Full_PreProcess(TicketDBModel):
        pass
    class zookeeper_Full_PreProcess(TicketDBModel):
        pass
    class openstack_Full_PreProcess(TicketDBModel):
        pass

    @classmethod
    def get_db_ref_by_system(cls, system_name):
        if system_name == 'cassandra':
            return cls.cassandra_Full_PreProcess
        elif system_name == 'flume':
            return cls.flume_Full_PreProcess
        elif system_name == 'hbase':
            return cls.hbase_Full_PreProcess
        elif system_name == 'hdfs':
            return cls.hdfs_Full_PreProcess
        elif system_name == 'mapreduce':
            return cls.mapreduce_Full_PreProcess
        elif system_name == 'zookeeper':
            return cls.zookeeper_Full_PreProcess
        elif system_name == 'openstack':
            return cls.openstack_Full_PreProcess
        else:
            return None


class Terse_PreProcessed_Keyword(TicketDBModel):
    class cassandra_Terse_PreProcess(TicketDBModel):
        pass
    class flume_Terse_PreProcess(TicketDBModel):
        pass
    class hbase_Terse_PreProcess(TicketDBModel):
        pass
    class hdfs_Terse_PreProcess(TicketDBModel):
        pass
    class mapreduce_Terse_PreProcess(TicketDBModel):
        pass
    class zookeeper_Terse_PreProcess(TicketDBModel):
        pass
    class openstack_Terse_PreProcess(TicketDBModel):
        pass

    @classmethod
    def get_db_ref_by_system(cls, system_name):
        if system_name == 'cassandra':
            return cls.cassandra_Terse_PreProcess
        elif system_name == 'flume':
            return cls.flume_Terse_PreProcess
        elif system_name == 'hbase':
            return cls.hbase_Terse_PreProcess
        elif system_name == 'hdfs':
            return cls.hdfs_Terse_PreProcess
        elif system_name == 'mapreduce':
            return cls.mapreduce_Terse_PreProcess
        elif system_name == 'zookeeper':
            return cls.zookeeper_Terse_PreProcess
        elif system_name == 'openstack':
            return cls.openstack_Terse_PreProcess
        else:
            return None


class Stemmed_Keyword(TicketDBModel):
    class cassandra_Stemmed_Keyword(TicketDBModel):
        pass
    class flume_Stemmed_Keyword(TicketDBModel):
        pass
    class hbase_Stemmed_Keyword(TicketDBModel):
        pass
    class hdfs_Stemmed_Keyword(TicketDBModel):
        pass
    class mapreduce_Stemmed_Keyword(TicketDBModel):
        pass
    class zookeeper_Stemmed_Keyword(TicketDBModel):
        pass
    class openstack_Stemmed_Keyword(TicketDBModel):
        pass


    @classmethod
    def get_db_ref_by_system(cls, system_name):
        if system_name == 'cassandra':
            return cls.cassandra_Stemmed_Keyword
        elif system_name == 'flume':
            return cls.flume_Stemmed_Keyword
        elif system_name == 'hbase':
            return cls.hbase_Stemmed_Keyword
        elif system_name == 'hdfs':
            return cls.hdfs_Stemmed_Keyword
        elif system_name == 'mapreduce':
            return cls.mapreduce_Stemmed_Keyword
        elif system_name == 'zookeeper':
            return cls.zookeeper_Stemmed_Keyword
        elif system_name == 'openstack':
            return cls.openstack_Stemmed_Keyword
        else:
            return None


class LFF_Keywords(TicketDBModel):
    class cassandra_LFF_Keywords(TicketDBModel):
        pass
    class flume_LFF_Keywords(TicketDBModel):
        pass
    class hbase_LFF_Keywords(TicketDBModel):
        pass
    class hdfs_LFF_Keywords(TicketDBModel):
        pass
    class mapreduce_LFF_Keywords(TicketDBModel):
        pass
    class zookeeper_LFF_Keywords(TicketDBModel):
        pass
    class openstack_LFF_Keywords(TicketDBModel):
        pass


    @classmethod
    def get_db_ref_by_system(cls, system_name):
        if system_name == 'cassandra':
            return cls.cassandra_LFF_Keywords
        elif system_name == 'flume':
            return cls.flume_LFF_Keywords
        elif system_name == 'hbase':
            return cls.hbase_LFF_Keywords
        elif system_name == 'hdfs':
            return cls.hdfs_LFF_Keywords
        elif system_name == 'mapreduce':
            return cls.mapreduce_LFF_Keywords
        elif system_name == 'zookeeper':
            return cls.zookeeper_LFF_Keywords
        elif system_name == 'openstack':
            return cls.openstack_LFF_Keywords
        else:
            return None
