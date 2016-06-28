from keyword_preprocess import process_system
from peewee import *
from stemmer import stem_system
from low_freq_filter import low_freq_filter
from generate_vectors import generate_vectors
from clustering import cluster
from jira import JIRA
import util


def main():
    #input_proc = raw_input("This will over-write system databases. Proceed? ").lower()
    #input_proc = 'y'
    #if input_proc != 'y':
    #    return

    options = {'server': 'https://issues.apache.org/jira'}
    #jira = JIRA(options=options)

    for system_name in util.systems:
        print system_name

        db = MySQLDatabase(system_name, user='root', passwd='mpcrrover')

        #process_system(db, jira, system_name)
        stem_system(db)
        low_freq_filter(db)
        generate_vectors(db)
        cluster(db)

        db.close()

if __name__ == '__main__':
    main()
