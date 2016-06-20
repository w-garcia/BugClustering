import nltk
import csv
import collections
from peewee import *

def generate_vectors(db):
    class LFF_Keywords(Model):
        description = TextField()
        classification = CharField()

        class Meta:
            database = db

    class Keyword_Vectors(LFF_Keywords):
        vectors = TextField()
        pass

    document_frequency_dict = collections.Counter()
    words_found = set()

    for row in LFF_Keywords.select():
        # Columns: row.description, row.classification
        words = nltk.word_tokenize(row.description)

        for word in words:
            word = word.encode('utf-8')
            # Only increment if the ticket contains an instance of the keyword (DF)
            if word not in words_found:
                words_found.add(word)
                document_frequency_dict[word] += 1
        words_found.clear()

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

    with open(str(db.database) + '_vectors.csv', 'w') as csvfile:
        fieldnames = document_frequency_dict.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_trouble_ticket_dicts:
            writer.writerow(row)

    #Keyword_Vectors.create_table()
    #with db.atomic():
    #    Keyword_Vectors.insert_many(list_trouble_ticket_dicts).execute()

    print "Generated vectors for " + str(db.database) + "."
