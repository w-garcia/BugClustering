from util import cwd
import util
from jira import *
from peewee import *


def get_full_description(j, line):
    begin_key = line.find('[') + 1
    end_key = line.find(']') - 1

    issue_id = line[begin_key: end_key + 1]
    try:
        issue = j.issue(issue_id)
    except JIRAError:
        print JIRAError.message
        return "", ""

    desc = issue.fields.description
    if desc is None:
        return "", ""

    paragraph_key = desc.find('\n') - 1

    return desc[:paragraph_key], desc


# noinspection PyTypeChecker
def process_system(db, jira, system):
    f = open(system + '.txt', 'r')
    if f is None:
        print "Couldn't find " + system + ". Aborting."
        return

    class Full_PreProcessed_Keywords(Model):
        description = TextField()
        classification = CharField()

        class Meta:
            database = db

    class Terse_PreProcessed_Keywords(Full_PreProcessed_Keywords):
        pass

    Full_PreProcessed_Keywords.create_table()
    Terse_PreProcessed_Keywords.create_table()

    list_classifications = []

    classifications_cache = {}
    terse_descriptions_cache = []
    full_descriptions_cache = []
    descriptions_processed_count = -1

    for line in f:
        if line.find('[') == 0:
            if descriptions_processed_count != -1:
                classifications_cache[descriptions_processed_count] = u' '.join(list_classifications).encode('utf-8')
                list_classifications = []

            ters_description, full_description = get_full_description(jira, line)
            line = line.replace(']\n', ' ')
            terse_descriptions_cache.append(u' '.join( (line, ters_description, ']\n') ).encode('utf-8'))
            full_descriptions_cache.append(u' '.join( (line, full_description, ']\n') ).encode('utf-8'))

            descriptions_processed_count += 1
            print "Processed bug description: " + str(descriptions_processed_count)

        elif line.startswith('a'):
            line = line.replace('\n', '')
            list_classifications.append(line.encode('utf-8'))

    # Reached eof, append last set of classifications
    classifications_cache[descriptions_processed_count] = u' '.join(list_classifications).encode('utf-8')

    populate_tables(Full_PreProcessed_Keywords, Terse_PreProcessed_Keywords, classifications_cache,
                    full_descriptions_cache, terse_descriptions_cache, db)

    print "Processed " + system + "."


def populate_tables(Full_PreProcessed_Keywords, Terse_PreProcessed_Keywords, classifications_cache,
                    full_descriptions_cache, terse_descriptions_cache, db):
    list_of_full_dicts = []
    list_of_ters_dicts = []

    for i in range(len(full_descriptions_cache)):
        list_of_full_dicts.append({'description': full_descriptions_cache[i], 'classification': classifications_cache[i]})
        list_of_ters_dicts.append({'description': terse_descriptions_cache[i],'classification': classifications_cache[i]})

    with db.atomic():
        Full_PreProcessed_Keywords.insert_many(list_of_full_dicts).execute()
        Terse_PreProcessed_Keywords.insert_many(list_of_ters_dicts).execute()
