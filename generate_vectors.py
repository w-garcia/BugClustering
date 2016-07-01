import nltk
import csv
import collections
import DBModel
import util


def generate_vectors(name, topology_filter, clustering_filter='none'):
    if topology_filter == 'none':
        selection = DBModel.LFF_Keywords.select()
    else: #topology_filter == 'system':
        selection = DBModel.LFF_Keywords.select_by_system(name)

    if clustering_filter == 'none':
        cluster_by_all(name, selection)
    else:
        # Filter by class specific filter (sw-, a-, hw-, etc.) or all classes if not specified
        cluster_by_filter(name, selection, clustering_filter)


def cluster_by_all(name, selection):
    list_of_descriptions = []

    for row in selection:
        list_of_descriptions.append(row.description)

    list_trouble_ticket_dicts = create_list_of_trouble_ticket_dicts(list_of_descriptions, name)

    if list_trouble_ticket_dicts is None:
        return

    vector_path = util.cwd + '/vectors/none/' + name + '/'
    util.ensure_path_exists(vector_path)

    # Write the matrix to csv file
    filename = vector_path + name + '_vectors.csv'
    write_matrix_file(filename, list_trouble_ticket_dicts)
    print "[Status] : Vector generated for {}.".format(name)


def cluster_by_filter(name, selection, class_key):
    class_to_list_of_descriptions_dict = collections.defaultdict(list)

    for row in selection:
        classes_to_keep = extract_classes_from_row(class_key, row)

        for c in classes_to_keep:
            class_to_list_of_descriptions_dict[c].append(row.description)

    for c in class_to_list_of_descriptions_dict:
        list_of_descriptions = class_to_list_of_descriptions_dict[c]

        list_trouble_ticket_dicts = create_list_of_trouble_ticket_dicts(list_of_descriptions, name, c)

        if list_trouble_ticket_dicts is None:
            return

        vector_path = util.cwd + '/vectors/class_filter/' + c + '/'
        util.ensure_path_exists(vector_path)

        # Write the matrix to csv file
        filename = vector_path + name + '_' + c + '_vectors.csv'
        write_matrix_file(filename, list_trouble_ticket_dicts)
        print "[Status] : Vector generated for {}.".format(c)


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


def create_list_of_trouble_ticket_dicts(list_of_descriptions, system_name, c='none'):
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

    if len(list_trouble_ticket_dicts) < 1:
        print "[Warning] : Not enough tickets to generate vectors. Skipping..."
        return None

    util.ensure_path_exists(util.cwd + '/vectors/')
    vector_path = util.cwd + '/vectors/'

    # Write file with word to DF to TF as columns
    with open(vector_path + system_name + '_' + c + '_' + '_word_DF+TF.csv', 'w') as csvfile_s:
        list_word_to_df_to_tf = []

        for word in document_frequency_dict.keys():
            temp_dict = {'Word': word, 'DF': document_frequency_dict[word], 'TF': term_frequency_dict[word]}
            list_word_to_df_to_tf.append(temp_dict)

        fieldnames = {'Word', 'DF', 'TF'}
        writer = csv.DictWriter(csvfile_s, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_word_to_df_to_tf:
            writer.writerow(row)

    print "[Vectors] : Wrote word to DF to TF file."

    return list_trouble_ticket_dicts


def write_matrix_file(filename, list_trouble_ticket_dicts):
    with open(filename, 'w') as csvfile:
        fieldnames = list_trouble_ticket_dicts[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_trouble_ticket_dicts:
            writer.writerow(row)