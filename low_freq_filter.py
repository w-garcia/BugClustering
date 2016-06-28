import nltk
import collections
from peewee import *
import util
import csv


def low_freq_filter(db):
    class Stemmed_Keywords(Model):
        description = TextField()
        classification = CharField()

        class Meta:
            database = db

    class LFF_Keywords(Stemmed_Keywords):
        pass

    word_to_count_dict = collections.Counter()
    doc_freq = collections.Counter()

    for row in Stemmed_Keywords.select():
        words_found = set()
        # Columns: row.description, row.classification
        words = nltk.word_tokenize(row.description)
        for word in words:
            if word not in words_found:
                words_found.add(word)
                doc_freq[word] += 1
            word_to_count_dict[word] += 1

        words_found.clear()

    list_of_lff_dicts = []
    words_to_keep_in_dataset = set()

    for row in Stemmed_Keywords.select():
        words_to_keep_in_ticket = []
        words = nltk.word_tokenize(row.description)
        for word in words:
            if word_to_count_dict[word] > 1 and doc_freq[word] > 1:
                words_to_keep_in_ticket.append(word)

                words_to_keep_in_dataset.add(word)

        list_of_lff_dicts.append({'description': u' '.join(words_to_keep_in_ticket), 'classification': row.classification})

    LFF_Keywords.create_table()

    #for row in list_of_lff_dicts:
    #    words = row['description'].split(' ')
    #    for word in words:
    #        print "TF: " + str(word_to_count_dict[word])
    #        print "DF: " + str(doc_freq[word])

    with db.atomic():
        LFF_Keywords.insert_many(list_of_lff_dicts).execute()

    util.ensure_path_exists(util.cwd + '/vectors/')
    vector_path = util.cwd + '/vectors/'

    # Write file with word to DF to TF as columns
    with open(vector_path + str(db.database) + '_word_DF+TF.csv', 'w') as csvfile_s:
        list_word_to_df_to_tf = []

        for word in words_to_keep_in_dataset:
            temp_dict = {'Word': word, 'DF': doc_freq[word], 'TF': word_to_count_dict[word]}
            list_word_to_df_to_tf.append(temp_dict)

        fieldnames = {'Word', 'DF', 'TF'}
        writer = csv.DictWriter(csvfile_s, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_word_to_df_to_tf:
            writer.writerow(row)

    print "Stripped " + str(db.database) + " of low frequency words."
    print "Wrote word to DF to TF file."

