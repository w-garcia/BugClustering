from util import cwd
import util
from jira import *
import DBModel


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
def process_system(jira, system):
    f = open(util.cwd + '/raw/' + system + '.txt', 'r')
    if f is None:
        print "Couldn't find " + system + ". Aborting."
        return

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
            # Append found description to the existing stub in the line, before the bracket.
            terse_descriptions_cache.append(u' '.join( (line, ters_description, ']\n') ).encode('utf-8'))
            full_descriptions_cache.append(u' '.join( (line, full_description, ']\n') ).encode('utf-8'))

            descriptions_processed_count += 1
            print "Processed bug description: " + str(descriptions_processed_count)

        elif line[0].isalpha():
            line = line.replace('\n', '')
            list_classifications.append(line.encode('utf-8'))


    # Reached eof, append last set of classifications
    classifications_cache[descriptions_processed_count] = u' '.join(list_classifications).encode('utf-8')

    populate_tables(classifications_cache, full_descriptions_cache, terse_descriptions_cache, system)

    print "Processed " + system + "."


def populate_tables(classifications_cache, full_descriptions_cache, terse_descriptions_cache, system):
    list_of_full_dicts = []
    list_of_ters_dicts = []

    for i in range(len(full_descriptions_cache)):
        list_of_full_dicts.append({'system': system,
                                   'description': full_descriptions_cache[i],
                                   'classification': classifications_cache[i]})

        list_of_ters_dicts.append({'system': system,
                                   'description': terse_descriptions_cache[i],
                                   'classification': classifications_cache[i]})

    DBModel.Full_PreProcessed_Keyword.overwrite_system_rows(system, list_of_full_dicts)

    DBModel.Terse_PreProcessed_Keyword.overwrite_system_rows(system, list_of_ters_dicts)
