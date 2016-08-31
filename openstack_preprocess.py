import util
from launchpadlib.launchpad import Launchpad
import DBModel
from httplib2 import ServerNotFoundError


def populate_tables(full_descriptions_cache, terse_descriptions_cache, status_cache, title_cache, issue_number_cache,
                    target_cache):
    # This will insert the cache lists into DB table without deleting. Cache lists must be cleared bef-orehand.
    list_of_full_dicts = []
    list_of_ters_dicts = []

    for i in range(len(full_descriptions_cache)):
        list_of_full_dicts.append({'system': 'openstack',
                                   'description': full_descriptions_cache[i],
                                   'classification': '',
                                   'title': title_cache[i],
                                   'status': status_cache[i],
                                   'issue_number': issue_number_cache[i],
                                   'target': target_cache[i]})

        list_of_ters_dicts.append({'system': 'openstack',
                                   'description': terse_descriptions_cache[i],
                                   'classification': '',
                                   'title': title_cache[i],
                                   'status': status_cache[i],
                                   'issue_number': issue_number_cache[i],
                                   'target': target_cache[i]})

    DBModel.Full_PreProcessed_Keyword.get_db_ref_by_system('openstack').insert_atomically(list_of_full_dicts)

    DBModel.Terse_PreProcessed_Keyword.get_db_ref_by_system('openstack').insert_atomically(list_of_ters_dicts)


def process_openstack():
    cachedir = util.cwd + "/launchpad_cache/"
    launchpad = Launchpad.login_anonymously('getting_tickets', 'production', cachedir, version='devel')

    openstack = launchpad.project_groups["openstack"]
    bugs = openstack.searchTasks(status=['New', 'Confirmed', 'Expired', 'Triaged', 'In Progress', 'Fix Released', 'Fix Committed'])
    # Possible: ['New', 'Confirmed', 'Expired', 'Triaged', 'In Progress', 'Fix Released', 'Fix Committed']
    i = 0
    choice = raw_input("This will completely delete openstack table. Proceed?").lower()
    if choice == 'n' or choice == 'no':
        return

    DBModel.Full_PreProcessed_Keyword.get_db_ref_by_system('openstack').reset_table()
    DBModel.Terse_PreProcessed_Keyword.get_db_ref_by_system('openstack').reset_table()

    terse_descriptions_cache = []
    full_descriptions_cache = []
    status_cache = []
    title_cache = []
    issue_id_cache = []
    target_cache = []

    print "[openstack] Starting openstack pre-processing."

    for bug in bugs:
        try:
            bugObj = launchpad.load(bug.bug_link)
        except ServerNotFoundError:
            print "ServerNotFoundError encountered by launchpadlib."
            print "Attempting to recover..."
            continue
        i += 1
        if i % 25 == 0:
            print "[openstack] {} bugs processed.".format(i)
        #if i == 20:
        #    break
        #print(sorted(bug.lp_attributes))
        #print "----"
        #print(sorted(bugObj.lp_attributes))
        #print "----"

        desc = bugObj.description
        paragraph_key = desc.find('\n') - 1

        ters_description = desc[:paragraph_key]
        full_description = desc

        terse_descriptions_cache.append(u''.join(ters_description).encode('utf-8'))
        full_descriptions_cache.append(u''.join(full_description).encode('utf-8'))
        status_cache.append(u''.join(bug.status).encode('utf-8'))
        title_cache.append(u''.join(bugObj.title).encode('utf-8'))
        issue_id_cache.append("{}".format(bugObj.id).encode('utf-8'))
        target_cache.append(u''.join(bug.bug_target_name).encode('utf-8'))

        if i % 500 == 0:
            populate_tables(full_descriptions_cache, terse_descriptions_cache, status_cache, title_cache,
                            issue_id_cache,
                            target_cache)
            terse_descriptions_cache = []
            full_descriptions_cache = []
            status_cache = []
            title_cache = []
            issue_id_cache = []
            target_cache = []
            print "Wrote 500 rows to openstack table."

    # Add the rest of the things
    populate_tables(full_descriptions_cache, terse_descriptions_cache, status_cache, title_cache, issue_id_cache,
                    target_cache)

    print "Processed openstack."
