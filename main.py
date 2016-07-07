from keyword_preprocess import process_system
from stemmer import stem_system
from low_freq_filter import low_freq_filter
from generate_vectors import generate_vectors
from clustering import cluster
from jira import JIRA
import util
import sys

def main():
    #input_proc = raw_input("This will over-write system databases. Proceed? ").lower()
    #input_proc = 'y'
    #if input_proc != 'y':
    #    return

    options = {'server': 'https://issues.apache.org/jira'}
    #jira = JIRA(options=options)

    filter_option = sys.argv[1].lower()
    cluster_option = sys.argv[2].lower()
    lff_threshold = int(sys.argv[3])
    max_tree_size = int(sys.argv[4])

    # Fill local database with data from each system
    for system_name in util.systems:
        print "[status] : " + system_name + " pre-processing started."

        #process_system(jira, system_name)
        #stem_system(system_name)
        #low_freq_filter(system_name, lff_threshold)

    # Perform clustering according to user specified granularity
    if filter_option == 'none':
        #generate_vectors("all_systems", filter_option, cluster_option)
        cluster("all_systems", filter_option, cluster_option, max_tree_size)
    else:
        for system_name in util.systems:
            generate_vectors(system_name, filter_option, cluster_option)
            cluster(system_name, filter_option, cluster_option, max_tree_size)


if __name__ == '__main__':
    main()
