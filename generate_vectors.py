import nltk
import csv
import collections
import DBModel
import util
from datetime import datetime


def generate_vectors(system_name, by_classes=False, by_system=False, class_key=None, by_class_mode="all"):

    if by_classes:
        generate_vectors_by_class(system_name, class_key, by_class_mode)
    if by_system:
        generate_vectors_by_system(system_name)

    # If both are false, print a warning.
    if (not by_system) and (not by_classes):
        print "[Warning] : No method to generate vectors chosen. No vectors generated."
    else:
        print "[Status] : Generated vectors for " + system_name + "."


def generate_vectors_by_system(system_name):
    list_of_descriptions = []

    for row in DBModel.LFF_Keywords.select_by_system(system_name):
        list_of_descriptions.append(row.description)

    list_trouble_ticket_dicts = create_list_of_trouble_ticket_dicts(list_of_descriptions)

    if len(list_trouble_ticket_dicts) < 1:
        print "[Warning] : Not enough tickets to generate vectors. Skipping..."
        return

    vector_path = util.cwd + '/vectors/by_system/' + system_name + '/'
    util.ensure_path_exists(vector_path)

    # Write the matrix to csv file
    filename = vector_path + system_name + '_vectors.csv'
    with open(filename, 'w') as csvfile:
        fieldnames = list_trouble_ticket_dicts[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_trouble_ticket_dicts:
            writer.writerow(row)


def generate_vectors_by_class(system_name, class_key, by_class_mode):
    class_to_list_of_descriptions_dict = collections.defaultdict(list)

    if by_class_mode == 'system':
        selection = DBModel.LFF_Keywords.select_by_system(system_name)
    else:
        selection = DBModel.LFF_Keywords.select()

    for row in selection:
        classes_to_keep = set()
        classes = row.classification.split(' ')

        for c in classes:
            c = c.encode()
            if len(c) < 2:
                continue
            elif class_key is None:
                classes_to_keep.add(c)
            elif c.startswith(class_key):
                classes_to_keep.add(c)

        for c in classes_to_keep:
            class_to_list_of_descriptions_dict[c].append(row.description)

    for c in class_to_list_of_descriptions_dict:
        list_of_descriptions = class_to_list_of_descriptions_dict[c]

        list_trouble_ticket_dicts = create_list_of_trouble_ticket_dicts(list_of_descriptions)

        if len(list_trouble_ticket_dicts) < 1:
            print "[Warning] : Not enough tickets to generate vectors. Skipping..."
            return

        vector_path = util.cwd + '/vectors/by_class/' + c + '/'
        util.ensure_path_exists(vector_path)

        # Write the matrix to csv file
        filename = vector_path + system_name + '_' + c + '_vectors.csv'
        with open(filename, 'w') as csvfile:
            fieldnames = list_trouble_ticket_dicts[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in list_trouble_ticket_dicts:
                writer.writerow(row)

        print "[Status] : Vector generated for {}.".format(c)


def create_list_of_trouble_ticket_dicts(list_of_descriptions):
    term_frequency_dict = collections.Counter()
    document_frequency_dict = collections.Counter()

    # Get TF and DF dicts for this list of description's dataset
    for description in list_of_descriptions:
        words = nltk.word_tokenize(description)
        words_found = set()

        for word in words:
            word = word.encode('utf-8')
            term_frequency_dict[word] += 1
            # Only increment if the ticket contains an instance of the keyword (DF)
            if word not in words_found:
                words_found.add(word)
                document_frequency_dict[word] += 1
        words_found.clear()
    list_trouble_ticket_dicts = []

    # With the DF dictionary, create the weight vector representing each ticket
    for description in list_of_descriptions:
        # Vector representing the ticket
        keyword_to_weight_dict = dict((keyword, 0) for keyword in document_frequency_dict.keys())
        words = nltk.word_tokenize(description)

        for word in words:
            word = word.encode('utf-8')
            if word not in words_found:
                words_found.add(word)
                keyword_to_weight_dict[word] = document_frequency_dict[word]
        words_found.clear()
        list_trouble_ticket_dicts.append(keyword_to_weight_dict)

    return list_trouble_ticket_dicts
