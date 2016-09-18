import csv
import DBModel
import util
from collections import defaultdict
from httplib2 import ServerNotFoundError
from launchpadlib.launchpad import Launchpad
from datetime import datetime, tzinfo , timedelta
from dateutil.parser import parse


class Bug:
    def __init__(self, target, bug_type, predict, time_delta, time_created, importance, heat=None):
        self.target = target
        self.bug_type = bug_type
        self.predict = predict
        self.time_delta = time_delta
        self.month_created = time_created.month
        self.year_created = time_created.year
        self.importance = importance
        self.heat = heat

    def change_target(self, new):
        self.target = new

ZERO = timedelta(0)


class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

utc = UTC()

list_id_to_class_dicts = defaultdict(str)
list_id_to_type_dicts = defaultdict(str)


with open('openstack_knn_classifier.csv', 'rb') as csvFile:
    reader = csv.DictReader(csvFile)
    list_of_dicts = [row for row in reader]

    for row in list_of_dicts:
        if row['id'] == '':
            continue
        num = int(row['id'])
        predict = row['prediction']
        type = row['t']
        list_id_to_class_dicts[num] = predict
        list_id_to_type_dicts[num] = type


select = DBModel.LFF_Keywords.get_db_ref_by_system('openstack').select()

list_bugs = []
set_of_targets = set()

for row in select:
    start = parse(row.date_created)
    if row.date_closed is None:
        continue
    else:
        end = parse(row.date_closed)

    delta = end-start

    target = row.target.encode('utf-8')
    if 'openstack' in row.target:
        target = 'meta'
    elif target != 'keystone' and target != 'heat' and target != 'cinder' and target != 'horizon' and target != 'neutron' and target != 'nova' and target != 'fuel' and target != 'meta':
        target = 'misc'

    set_of_targets.add(target)

    importance = row.importance
    if row.importance == 'Undecided' or row.importance == 'Wishlist':
        importance = 'N/A'

    temp = Bug(target,
               list_id_to_type_dicts[int(row.id)],
               list_id_to_class_dicts[int(row.id)],
               delta.days, start, importance, int(row.heat))
    list_bugs.append(temp)


def create_time_series():
    month_date_bug_types = defaultdict(dict)

    for bug in list_bugs:
        quarter = (bug.month_created - 1)//3 + 1
        index = '{}-{}{}'.format(bug.year_created, 'Q', quarter)
        month_date_bug_types[index]['t-new'] = 0
        month_date_bug_types[index]['t-bug'] = 0

    for bug in list_bugs:
        quarter = (bug.month_created - 1)//3 + 1
        index = '{}-{}{}'.format(bug.year_created, 'Q', quarter)
        month_date_bug_types[index][bug.bug_type] += 1

    list_type_dicts = []

    for key in sorted(month_date_bug_types):
        temp = {'period': key,
                't-new': month_date_bug_types[key]['t-new'],
                't-bug': month_date_bug_types[key]['t-bug']}
        list_type_dicts.append(temp)

    with open(util.cwd + '/target_bugs_to_time.csv', 'wb') as csvWrite:
        fieldnames = list_type_dicts[0].keys()
        writer = csv.DictWriter(csvWrite, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(list_type_dicts)

#create_time_series()


def create_importance_chart():
    importance_to_type_list = defaultdict(dict)

    for bug in list_bugs:
        importance_to_type_list[bug.importance]['t-bug'] = 0
        importance_to_type_list[bug.importance]['t-new'] = 0

    for bug in list_bugs:
        importance_to_type_list[bug.importance][bug.bug_type] += 1

    list_type_dicts = []
    for key in sorted(importance_to_type_list):
        temp = {'importance': key,
                't-new': importance_to_type_list[key]['t-new'],
                't-bug': importance_to_type_list[key]['t-bug']}
        list_type_dicts.append(temp)

    with open(util.cwd + '/target_importance_to_type.csv', 'wb') as csvWrite:
        fieldnames = list_type_dicts[0].keys()
        writer = csv.DictWriter(csvWrite, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(list_type_dicts)

#create_importance_chart()


def create_heat_chart():
    heat_to_type_list = defaultdict(dict)

    for bug in list_bugs:
        heat_to_type_list[bug.heat]['t-bug'] = 0
        heat_to_type_list[bug.heat]['t-new'] = 0

    for bug in list_bugs:
        heat_to_type_list[bug.heat][bug.bug_type] += 1

    list_type_dicts = []
    for key in sorted(heat_to_type_list):
        temp = {'heat': key,
                't-new': heat_to_type_list[key]['t-new'],
                't-bug': heat_to_type_list[key]['t-bug']}
        list_type_dicts.append(temp)

    with open(util.cwd + '/target_heat_to_type.csv', 'wb') as csvWrite:
        fieldnames = list_type_dicts[0].keys()
        writer = csv.DictWriter(csvWrite, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(list_type_dicts)


create_heat_chart()


def create_heat_to_importance():
    heat_to_importance_list = defaultdict(dict)

    for bug in list_bugs:
        heat_to_importance_list[bug.heat]['Low'] = 0
        heat_to_importance_list[bug.heat]['Medium'] = 0
        heat_to_importance_list[bug.heat]['High'] = 0
        heat_to_importance_list[bug.heat]['Critical'] = 0
        heat_to_importance_list[bug.heat]['N/A'] = 0

    for bug in list_bugs:
        if bug.importance == 'Wishlist' or bug.importance == 'Undecided':
            continue
        heat_to_importance_list[bug.heat][bug.importance] += 1

    list_type_dicts = []
    for key in sorted(heat_to_importance_list):
        temp = {'heat': key}
        temp.update(heat_to_importance_list[key])
        list_type_dicts.append(temp)

    with open(util.cwd + '/target_heat_to_importance.csv', 'wb') as csvWrite:
        fieldnames = list_type_dicts[0].keys()
        writer = csv.DictWriter(csvWrite, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(list_type_dicts)


#create_heat_to_importance()


def create_time_delta():
    time_delta_to_type = defaultdict(dict)

    for bug in list_bugs:
        time_delta_to_type[bug.time_delta]['t-bug'] = 0
        time_delta_to_type[bug.time_delta]['t-new'] = 0

    for bug in list_bugs:
        time_delta_to_type[bug.time_delta][bug.bug_type] += 1

    list_type_dicts = []
    for key in sorted(time_delta_to_type):
        temp = {'Time to Close': key}
        temp.update(time_delta_to_type[key])
        list_type_dicts.append(temp)

    with open(util.cwd + '/target_ttc_to_type.csv', 'wb') as csvWrite:
        fieldnames = list_type_dicts[0].keys()
        writer = csv.DictWriter(csvWrite, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(list_type_dicts)

#create_time_delta()


def create_importance_to_module():
    importance_to_target_list = defaultdict(dict)

    for bug in list_bugs:
        importance_to_target_list[bug.importance][bug.target] = 0

    for bug in list_bugs:
        importance_to_target_list[bug.importance][bug.target] += 1

    print importance_to_target_list

    list_type_dicts = []
    for key in sorted(importance_to_target_list):
        temp = {'importance': key}
        temp.update(importance_to_target_list[key])
        list_type_dicts.append(temp)

    with open(util.cwd + '/target_importance_to_target.csv', 'wb') as csvWrite:
        fieldnames = ['importance']
        fieldnames.extend(set_of_targets)
        writer = csv.DictWriter(csvWrite, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(list_type_dicts)

#create_importance_to_module()


def create_module_to_type():
    module_to_type = defaultdict(dict)

    for bug in list_bugs:
        module_to_type[bug.target]['t-bug'] = 0
        module_to_type[bug.target]['t-new'] = 0

    for bug in list_bugs:
        module_to_type[bug.target][bug.bug_type] += 1

    print module_to_type

    list_type_dicts = []
    for key in sorted(module_to_type):
        temp = {'module': key}
        temp.update(module_to_type[key])
        list_type_dicts.append(temp)

    with open(util.cwd + '/target_module_to_type.csv', 'wb') as csvWrite:
        fieldnames = list_type_dicts[0].keys()
        writer = csv.DictWriter(csvWrite, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(list_type_dicts)

#create_module_to_type()
"""
list_dicts = []

with open(util.cwd + '/target_bugs_to_time.csv', 'wb') as csvWrite:
    fieldnames = list_dicts[0].keys()
    writer = csv.DictWriter(csvWrite, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(list_dicts)
"""

"""
list_dicts = []
counter = defaultdict(int)
kappa = defaultdict(int)

tnewcounter = defaultdict(int)
tbugcounter = defaultdict(int)

swcounter = defaultdict(int)
hwcounter = defaultdict(int)

for r in select:
    counter[r.target] += 1
    predict = list_id_to_class_dicts[int(r.id)]
    type = list_id_to_type_dicts[int(r.id)]

    if type == 't-new':
        tnewcounter[r.target] += 1
    else:
        tbugcounter[r.target] += 1

    if predict == 'sw-':
        swcounter[r.target] += 1
    else:
        hwcounter[r.target] += 1

for i in counter:
    if counter[i] < 10:
        kappa['misc'] += counter[i]
        tbugcounter['misc'] += tbugcounter[i]
        tnewcounter['misc'] += tnewcounter[i]
        swcounter['misc'] += swcounter[i]
        hwcounter['misc'] += hwcounter[i]
    else:
        if 'openstack' in i:
            kappa['openstack-meta'] += counter[i]
            tbugcounter['openstack-meta'] += tbugcounter[i]
            tnewcounter['openstack-meta'] += tnewcounter[i]
            swcounter['openstack-meta'] += swcounter[i]
            hwcounter['openstack-meta'] += hwcounter[i]

        else:
            kappa[i] = counter[i]

for i in kappa:
    list_dicts.append({'id': i, 'count': kappa[i],
                       'tbug': tbugcounter[i], 'tnew': tnewcounter[i],
                       'sw': swcounter[i], 'hw': hwcounter[i]})

with open(util.cwd + '/target_list_to_classes.csv', 'wb') as csvWrite:
    fieldnames = list_dicts[0].keys()
    writer = csv.DictWriter(csvWrite, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(list_dicts)
"""