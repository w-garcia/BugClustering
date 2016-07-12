import nltk
import collections
import DBModel
import util
import csv
from config import config as cfg


def low_freq_filter(system_name):
    word_to_count_dict = collections.Counter()
    doc_freq = collections.Counter()

    for row in DBModel.Stemmed_Keyword.select_by_system(system_name):
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

    lff_threshold = cfg.low_freq_threshold

    for row in DBModel.Stemmed_Keyword.select_by_system(system_name):
        words_to_keep_in_ticket = []
        words = nltk.word_tokenize(row.description)
        for word in words:
            if word_to_count_dict[word] >= lff_threshold and doc_freq[word] >= lff_threshold:
                words_to_keep_in_ticket.append(word)

                words_to_keep_in_dataset.add(word)

        list_of_lff_dicts.append({'system': system_name,
                                  'description': u' '.join(words_to_keep_in_ticket),
                                  'classification': row.classification})

    DBModel.LFF_Keywords.overwrite_system_rows(system_name, list_of_lff_dicts)

    print "Stripped " + system_name + " of low frequency words."

