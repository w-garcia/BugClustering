import DBModel
systems = ['cassandra', 'flume', 'hbase', 'hdfs', 'mapreduce', 'zookeeper']


def to_dict(selection):
    list_of_dicts = []
    for row in selection:
        dict = {'description': row.description, 'classification': row.classification, 'system': row.system}
        list_of_dicts.append(dict)
    return list_of_dicts


for system in systems:
    full_select = DBModel.Full_PreProcessed_Keyword.select_by_system(system)
    ters_select = DBModel.Terse_PreProcessed_Keyword.select_by_system(system)
    stem_select = DBModel.Stemmed_Keyword.select_by_system(system)
    lff_select = DBModel.LFF_Keywords.select_by_system(system)

    DBModel.Full_PreProcessed_Keyword.get_db_ref_by_system(system).overwrite_system_rows(system, to_dict(full_select))
    DBModel.Terse_PreProcessed_Keyword.get_db_ref_by_system(system).overwrite_system_rows(system, to_dict(ters_select))
    DBModel.Stemmed_Keyword.get_db_ref_by_system(system).overwrite_system_rows(system, to_dict(stem_select))
    DBModel.LFF_Keywords.get_db_ref_by_system(system).overwrite_system_rows(system, to_dict(lff_select))





