from generate_vectors import generate_vectors
from clustering import cluster
from config import config as cfg
import csv
import DBModel
import util
import copy


def classify():
    #TODO: Get in random order, sequential tickets might be similair (important when processing multiple tickets at once)
    if cfg.clustering_mode == 'test':
        _dataset_stack = [row for row in DBModel.LFF_Keywords.select_by_system(cfg.test_dataset)]
    if cfg.clustering_mode == 'label':
        _dataset_stack = [row for row in DBModel.LFF_Keywords.select_by_system(cfg.labelling_dataset)]

    list_of_dicts = []

    while _dataset_stack:
        print "[classifier] : {} tickets left to go.".format(len(_dataset_stack))
        row = _dataset_stack.pop()
        row_copy = copy.deepcopy(row)
        #TODO: change prediction variable such that I can pass in a list of addon rows and get a list of predictions
        prediction = []
        generate_vectors(cfg.model_selection, row_copy)
        cluster(cfg.model_selection, prediction)

        _row_dict = {'id': row.id, 'description': row.description,
                     'system': row.system, 'ground truth': row.classification, 'prediction': ' '.join(prediction[0])}
        list_of_dicts.append(_row_dict)

    cls_path = util.generate_meta_path(cfg.model_selection, 'classifier')
    util.ensure_path_exists(cls_path)
    filename = cls_path + list_of_dicts[0]['system'] + '_classifier.csv'
    write_classifier_file(filename, list_of_dicts)
    print "[status] : Classifier finished. Analysis started."

    filename = cls_path + list_of_dicts[0]['system'] + '_statistics.csv'


def write_classifier_file(filename, list_of_dicts):
    with open(filename, 'w') as csvfile:
        fieldnames = list_of_dicts[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_of_dicts:
            writer.writerow(row)


def generate_statistics(list_of_dicts):
    _list_truths = [row['ground truth'] for row in list_of_dicts]
    _list_predictions = [row['prediction'] for row in list_of_dicts]

    _total_category_accuracy = 0.0
    for i in range(len(list_of_dicts)):
        category_accuracy_count = 0.0
        class_accuracy_count = 0.0

        _truths = set(_list_truths[i].split(' '))
        _truths_of_interest = set()
        _predictions = set(_list_predictions[i].split(' '))
        _truth_categories = set()

        # First, fill in the class categories of interest from config in the truth list
        for ci in cfg.classes_of_interest:
            for truth in _truths:
                if ci in truth:
                    _truth_categories.add(ci)
                    _truths_of_interest.add(truth)
        print "[analysis] : Truth categories for ticket {}: {}".format(i, _truth_categories)

        # Compare across categories
        for c in _predictions:
            for tc in _truth_categories:
                if c == tc:
                    category_accuracy_count += 1
        _total_category_accuracy += float(category_accuracy_count / len(_truth_categories))



    category_accuracy = float(_total_category_accuracy / len(list_of_dicts))
    print "[analysis] : Category accuracy: {}".format(category_accuracy)


def write_statistics_file(filename, (category_accuracy, class_accuracy)):
    pass