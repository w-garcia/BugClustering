import nltk
import csv
import collections
import DBModel
import util


def generate_vectors(system_name, byClasses=False):
    class_to_list_of_descriptions_dict = collections.defaultdict(list)

    for row in DBModel.LFF_Keywords.select_by_system(system_name):
        # Columns: row.description, row.classification
        #words = nltk.word_tokenize(row.description)
        classes = row.classification.split(' ')

        """
        for word in words:
            word = word.encode('utf-8')
            term_frequency_dict[word] += 1
            # Only increment if the ticket contains an instance of the keyword (DF)
            if word not in words_found:
                words_found.add(word)
                document_frequency_dict[word] += 1
        words_found.clear()
        """
        for c in classes:
            if len(c) < 2:
                classes.remove(c)

        for c in classes:
            class_to_list_of_descriptions_dict[c].append(row.description)

    for c in class_to_list_of_descriptions_dict:
        term_frequency_dict = collections.Counter()
        document_frequency_dict = collections.Counter()

        # Get TF and DF dicts for this classification's dataset
        for description in class_to_list_of_descriptions_dict[c]:
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
        for description in class_to_list_of_descriptions_dict[c]:
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

        util.ensure_path_exists(util.cwd + '/vectors/')
        vector_path = util.cwd + '/vectors/'

        # Write the matrix to csv file
        with open(vector_path + system_name + '_' + c + '_vectors.csv', 'w') as csvfile:
            fieldnames = document_frequency_dict.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in list_trouble_ticket_dicts:
                writer.writerow(row)

        """
        # Write file with word to DF to TF as columns
        with open(vector_path + str(db.database) + '_' + c + '_word_DF+TF.csv', 'w') as csvfile_s:
            list_word_to_df_to_tf = []

            for word in document_frequency_dict:
                temp_dict = {'Word': word, 'DF': document_frequency_dict[word], 'TF': term_frequency_dict[word]}
                list_word_to_df_to_tf.append(temp_dict)

            fieldnames = {'Word', 'DF', 'TF'}
            writer = csv.DictWriter(csvfile_s, fieldnames=fieldnames)

            writer.writeheader()
            for row in list_word_to_df_to_tf:
                writer.writerow(row)
        """
    """
    list_trouble_ticket_dicts = []

    for row in LFF_Keywords.select():
        ticket_weight_vector = dict((keyword, 0) for keyword in document_frequency_dict.keys())
        words = nltk.word_tokenize(row.description)

        for word in words:
            word = word.encode('utf-8')
            if word not in words_found:
                words_found.add(word)
                ticket_weight_vector[word] = document_frequency_dict[word]
        words_found.clear()
        list_trouble_ticket_dicts.append(ticket_weight_vector)

    util.ensure_path_exists(util.cwd + '/vectors/')
    vector_path = util.cwd + '/vectors/'
    with open(vector_path + str(db.database) + '_vectors.csv', 'w') as csvfile:
        fieldnames = document_frequency_dict.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_trouble_ticket_dicts:
            writer.writerow(row)

    with open(vector_path + str(db.database) + '_word_DF+TF.csv', 'w') as csvfile_s:
        list_word_to_df_to_tf = []

        for word in document_frequency_dict:
            temp_dict = {'Word': word, 'DF': document_frequency_dict[word], 'TF': term_frequency_dict[word]}
            list_word_to_df_to_tf.append(temp_dict)

        fieldnames = list_word_to_df_to_tf[0].keys()
        writer = csv.DictWriter(csvfile_s, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_word_to_df_to_tf:
            writer.writerow(row)
    """

    print "Generated vectors for " + system_name + "."
