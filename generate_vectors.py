from config import config as cfg
import nltk
import csv
import collections
import DBModel
import util
import math
from Ticket import Ticket

def generate_vectors(name):
    systems_filter = cfg.systems_filter
    class_clustering_filter = cfg.class_clustering_filter

    if systems_filter == 'none':
        selection = DBModel.LFF_Keywords.select()
    else: #systems_filter == 'system':
        selection = DBModel.LFF_Keywords.select_by_system(name)

    if class_clustering_filter == 'none':
        cluster_by_all(name, selection)
    else:
        # Filter by class specific filter (sw-, a-, hw-, etc.) or all classes if not specified
        cluster_by_filter(name, selection, class_clustering_filter)


def cluster_by_all(name, selection):
    list_of_tickets = []

    for row in selection:
        t = Ticket(row.id, row.description, row.classification, row.system)

        list_of_tickets.append(t)

    list_ticket_dicts = []
    create_list_of_trouble_ticket_dicts(list_of_tickets, name, list_ticket_dicts)

    if len(list_ticket_dicts) < 1:
        return

    vector_path = util.generate_meta_path(name, 'vectors')
    util.ensure_path_exists(vector_path)

    # Write the matrix to csv file
    filename = vector_path + name + '_vectors.csv'
    write_matrix_file(filename, list_ticket_dicts)
    print "[status] : Vector generated for {}.".format(name)


def cluster_by_filter(name, selection, class_key):
    class_to_list_of_tickets_dict = collections.defaultdict(list)

    # Create ground truth vectors for each class
    for row in selection:
        classes_to_keep = extract_classes_from_row(class_key, row)

        # Add the filter of interest to build a non-truth list
        classes_to_keep.add(class_key)

        for c in classes_to_keep:
            t = Ticket(row.id, row.description, row.classification, row.system)
            class_to_list_of_tickets_dict[c].append(t)

    for c in class_to_list_of_tickets_dict:
        _list_of_tickets = class_to_list_of_tickets_dict[c]

        list_ticket_dicts = []
        create_list_of_trouble_ticket_dicts(_list_of_tickets, name, list_ticket_dicts, c)

        if len(list_ticket_dicts) < 1:
            return

        vector_path = util.generate_meta_path(name, 'vectors', c)
        util.ensure_path_exists(vector_path)

        # Write the matrix to csv file
        filename = vector_path + name + '_vectors.csv'
        write_matrix_file(filename, list_ticket_dicts)
        print "[status] : Vector generated for {}.".format(c)


def extract_classes_from_row(class_key, row):
    classes = row.classification.split(' ')
    classes_to_keep = set()
    for c in classes:
        c = c.encode()
        if len(c) < 2:
            continue
        elif class_key is 'none':
            classes_to_keep.add(c)
        elif c.startswith(class_key):
            classes_to_keep.add(c)
    return classes_to_keep


def create_list_of_trouble_ticket_dicts(list_of_tickets, system_name, list_ticket_dicts, c='none'):
    term_frequency_dict = collections.Counter()
    document_frequency_dict = collections.Counter()

    weighting_scheme = cfg.weighting_scheme

    # Get TF and DF dicts for this dataset
    create_dictionaries(document_frequency_dict, list_of_tickets, term_frequency_dict)

    # With the DF dictionary, create the weight vector representing each ticket
    # TODO: Might be a spot for further optimization
    for ticket in list_of_tickets:
        words_found = set()

        # Vector representing the ticket
        keyword_to_weight_dict = dict((keyword, 0) for keyword in document_frequency_dict.keys())
        words = nltk.word_tokenize(ticket.description)

        for word in words:
            word = word.encode('utf-8')
            if word not in words_found:
                words_found.add(word)

                # Assign weight to word, whatever it may be
                DF = float(document_frequency_dict[word])
                IDF = 1.0 / (1.0 + DF) # Adjust for 0 denominator
                TF = float(term_frequency_dict[word])
                if weighting_scheme == 'DF':
                    keyword_to_weight_dict[word] = DF
                elif weighting_scheme == 'TFxIDF':
                    keyword_to_weight_dict[word] = TF*IDF

        # Parameterize the numeric weights as a list of strings
        list_weights = [str(x) for x in keyword_to_weight_dict.values()]
        list_keywords = [word for word in keyword_to_weight_dict.keys() if keyword_to_weight_dict[word] > 0]

        # Create dictionary representing this ticket
        _ticket_dict = {'id': ticket.id, 'description': ticket.description,
                        'classification': ticket.classes, 'system': ticket.system,
                        'vector': ' '.join(list_weights), 'keywords': ' '.join(list_keywords)}
        list_ticket_dicts.append(_ticket_dict)

    if len(list_ticket_dicts) < 1:
        print "[warning] : Not enough tickets to generate vectors. Skipping..."
        return

    vector_path = util.generate_meta_path(system_name, 'vectors', c)
    util.ensure_path_exists(vector_path)

    # Write file with word to DF to TF as columns
    with open(vector_path + system_name + '_word_DF+TF+IDF+TF*IDF.csv', 'w') as csvfile_s:
        list_word_to_weights = []

        for word in document_frequency_dict.keys():
            DF = float(document_frequency_dict[word])
            IDF = 1.0 / (1.0 + DF) # Adjust for 0 denominator
            TF = float(term_frequency_dict[word])
            temp_dict = {'Word': word, 'DF': DF, 'TF': TF, 'IDF': IDF, 'TF*IDF': TF*IDF}
            list_word_to_weights.append(temp_dict)

        fieldnames = {'Word', 'DF', 'TF', 'IDF', 'TF*IDF'}
        writer = csv.DictWriter(csvfile_s, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_word_to_weights:
            writer.writerow(row)

    print "[{}] : Wrote word to weights file.".format(system_name)


def create_dictionaries(document_frequency_dict, list_of_tickets, term_frequency_dict):
    for ticket in list_of_tickets:
        words = nltk.word_tokenize(ticket.description)
        words_found = set()

        for word in words:
            word = word.encode('utf-8')
            term_frequency_dict[word] += 1
            # Only increment if the ticket contains an instance of the keyword (DF)
            if word not in words_found:
                words_found.add(word)
                document_frequency_dict[word] += 1


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def write_matrix_file(filename, list_of_dicts):
    with open(filename, 'w') as csvfile:
        fieldnames = list_of_dicts[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_of_dicts:
            writer.writerow(row)