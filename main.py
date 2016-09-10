from keyword_preprocess import process_system
from stemmer import stem_system
from low_freq_filter import low_freq_filter
from generate_vectors import generate_vectors
from clustering_h_agglomerative import do_h_agglomerative
from config import config as cfg
from jira import JIRA
from classifier import classify
from openstack_preprocess import process_openstack
import util
import sys
from analyzer import analyze
import numpy


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
            do_h_agglomerative("all_systems")
        else:
            for system_name in util.systems:
                generate_vectors(system_name)
                do_h_agglomerative(system_name)
    else:
        print "[status] : {} clustering mode started with {} slice selecton.".format(cfg.clustering_mode, cfg.xvalidation_mode)
        # Perform cross validation based on config: either k-fold or random sub-sampling
        if cfg.xvalidation_mode == 'kfold':
            cat_accuracy_total = 0
            cat_accuracies = []
            class_accuracy_total = 0
            class_accuracies = []
            knn_cat_accuracy_total = 0
            knn_cat_accuracies = []
            knn_class_accuracy_total = 0
            knn_class_accuracies = []
            for i in range(int(1 / cfg.test_dataset_split)):
                print "[kfold] : Classifying slice {}".format(i)
                classify(slice=i)
                scores_matrix = analyze(return_accuracies=True)
                cat_accuracy_total += scores_matrix[0][0]
                cat_accuracies.append(scores_matrix[0][0])
                if scores_matrix[0][1] != 'nil':
                    class_accuracy_total += scores_matrix[0][1]
                    class_accuracies.append(scores_matrix[0][1])
                knn_cat_accuracy_total += scores_matrix[1][0]
                knn_cat_accuracies.append(scores_matrix[1][0])
                if scores_matrix[1][1] != 'nil':
                    knn_class_accuracy_total += scores_matrix[1][1]
                    knn_class_accuracies.append(scores_matrix[1][1])
            print "h-agglomerative - "
            cat_accuracy = cat_accuracy_total / int(1 / cfg.test_dataset_split)
            cat_std = numpy.std(cat_accuracies)
            class_accuracy = class_accuracy_total / int(1 / cfg.test_dataset_split)
            class_std = numpy.std(class_accuracies)
            print "category: {} std: {} class: {} std: {}".format(cat_accuracy, cat_std,
                                                                  class_accuracy, class_std)
            print "knn - "
            knn_cat_accuracy = knn_cat_accuracy_total / int(1 / cfg.test_dataset_split)
            knn_cat_std = numpy.std(knn_cat_accuracies)
            knn_class_accuracy = knn_class_accuracy_total / int(1 / cfg.test_dataset_split)
            knn_class_std = numpy.std(knn_class_accuracies)
            print "category: {} std: {} class: {} std: {}".format(knn_cat_accuracy, knn_cat_std,
                                                                  knn_class_accuracy, knn_class_std)

        elif cfg.xvalidation_mode == 'rand_ss':
            classify()
            analyze()

if __name__ == '__main__':
    main()
