from keyword_preprocess import process_system
from stemmer import stem_system
from low_freq_filter import low_freq_filter
from generate_vectors import generate_vectors
from clustering import cluster
from config import config as cfg
from jira import JIRA
from classifier import classify
import util
import sys
from analyzer import analyze

def main():
    systems_filter = cfg.systems_filter
    perform_preprocessing = cfg.perform_preprocessing

    # Fill local database with data from each system
    if perform_preprocessing:
        options = {'server': 'https://issues.apache.org/jira'}
        jira = JIRA(options=options)

        for system_name in util.systems:
            print "[status] : " + system_name + " pre-processing started."
            process_system(jira, system_name)
            stem_system(system_name)
            low_freq_filter(system_name)

    # Perform clustering according to user specified granularity
    if cfg.clustering_mode == 'vanilla':
        print "[status] : vanilla clustering mode started."
        if systems_filter == 'none':
            generate_vectors("all_systems")
            cluster("all_systems")
        else:
            for system_name in util.systems:
                generate_vectors(system_name)
                cluster(system_name)
    else:
        print "[status] : {} clustering mode started.".format(cfg.clustering_mode)
        #classify()
        analyze()

if __name__ == '__main__':
    main()
