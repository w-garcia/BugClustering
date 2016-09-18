import csv
import DBModel
import util
from collections import defaultdict
from httplib2 import ServerNotFoundError
from launchpadlib.launchpad import Launchpad


def save_extra_data():
    cachedir = util.cwd + "/launchpad_cache/"
    launchpad = Launchpad.login_anonymously('getting_tickets', 'production', cachedir, version='devel')

    openstack = launchpad.project_groups["openstack"]
    #bugs = openstack.searchTasks(status=['New', 'Confirmed', 'Expired', 'Triaged', 'In Progress', 'Fix Released', 'Fix Committed'])
    # Possible: ['New', 'Confirmed', 'Expired', 'Triaged', 'In Progress', 'Fix Released', 'Fix Committed']
    i = 0

    select = DBModel.Terse_PreProcessed_Keyword.get_db_ref_by_system('openstack').random('openstack')

    for row in select:
        if row.status == 'New' or row.status == 'Expired' or row.status == 'In Progress':
            continue

        """
        if 'openstack' in row.target:
            target = 'meta'
        else:
            target = row.target
        if target != 'keystone' and target != 'heat' and target != 'cinder' and target != 'horizon' and target != 'neutron' and target != 'nova' and target != 'fuel' and target != 'meta':
            continue
        """

        issue_num = int(row.issue_number)
        try:
            cachedir = util.cwd + "/launchpad_cache/"
            launchpad = Launchpad.login_anonymously('getting_tickets', 'production', cachedir, version='devel')
            #openstack = launchpad.project_groups["openstack"]
            bug = launchpad.bugs[issue_num]
            task_entry = launchpad.load(bug.bug_tasks_collection_link).entries[0]

        except ServerNotFoundError:
            print "ServerNotFoundError encountered by launchpadlib."
            print "Attempting to recover..."
            continue

        row.date_created = bug.date_created
        if task_entry['date_closed'] is None:
            continue
        row.description = bug.description
        row.date_closed = task_entry['date_closed']
        row.heat = bug.heat
        row.importance = task_entry['importance'].encode('utf-8')
        row.save()

        i += 1
        if i % 30000 == 0:
            break
        #    #print "[openstack] {} bugs processed.".format(i)
        print i

        #if i == 20:
        #    break
        #print (bug.title)
        #print(bug.heat)
        #print(task_entry['importance'].encode('utf-8'))
        #print (bug.date_created)
        #print(task_entry['date_closed'])
        #print(sorted(bug.lp_attributes))
        #print "----"
        #print(sorted(bugObj.lp_attributes))
        #print "----"

save_extra_data()