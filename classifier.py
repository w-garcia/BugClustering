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
        if cfg.test_dataset == cfg.model_selection:
            # Split up the same dataset
            pass
        _dataset_stack = [row for row in DBModel.LFF_Keywords.get_db_ref_by_system(cfg.test_dataset).select()]
    if cfg.clustering_mode == 'label':
        if cfg.labelling_dataset == cfg.model_selection:
            pass
        _dataset_stack = [row for row in DBModel.LFF_Keywords.get_db_ref_by_system(cfg.labelling_dataset).select()]

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



def write_classifier_file(filename, list_of_dicts):
    with open(filename, 'w') as csvfile:
        fieldnames = list_of_dicts[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_of_dicts:
            writer.writerow(row)


