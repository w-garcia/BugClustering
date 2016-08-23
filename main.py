from keyword_preprocess import process_system
from stemmer import stem_system
from low_freq_filter import low_freq_filter
from generate_vectors import generate_vectors
from clustering import cluster
from config import config as cfg
from jira import JIRA
from classifier import classify
from openstack_preprocess import process_openstack
import util
import sys
from analyzer import analyze


def main():
    systems_filter = cfg.systems_filter
    perform_preprocessing = cfg.perform_preprocessing
    retrieve_labelling_datasets = cfg.retrieve_label_datasets

    # Fill local database with data from each system
    if perform_preprocessing:
        options = {'server': 'https://issues.apache.org/jira'}
        jira = JIRA(options=options)

        for system_name in util.systems:
            print "[status] : " + system_name + " pre-processing started."
            #process_system(jira, system_name)
            stem_system(system_name)
            low_freq_filter(system_name)

    if retrieve_labelling_datasets:
        process_openstack()
        stem_system('openstack')
        low_freq_filter('openstack')

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
        # Perform cross validation based on config: either k-fold or random sub-sampling
        if cfg.xvalidation_mode == 'kfold':
            cat_accuracy_total = 0
            class_accuracy_total = 0
            for i in range(int(1 / cfg.test_dataset_split)):
                print "[kfold] : Classifying slice {}".format(i)
                classify(slice=i)
                category_score, class_score = analyze(return_accuracies=True)
                cat_accuracy_total += category_score
                class_accuracy_total += class_score
            print "category: {} class: {}".format(cat_accuracy_total / int(1 / cfg.test_dataset_split),
                                                  class_accuracy_total / int(1 / cfg.test_dataset_split))
        elif cfg.xvalidation_mode == 'rand_ss':
            classify()
            analyze()

if __name__ == '__main__':
    main()
