from generate_vectors import generate_vectors
from clustering import cluster
from config import config as cfg
import csv
import DBModel
import util
import copy
import random


def classify():

    _dataset_stack, selection_cache = setup_datasets()

    list_of_dicts = []

    while _dataset_stack:
        print "[classifier] : {} tickets left to go.".format(len(_dataset_stack))
        row = _dataset_stack.pop()
        row_copy = copy.deepcopy(row)
        row_copy.classification = ''

        assert(uniqueness_condition(selection_cache, row_copy),
                "Classifier bug ticket is not unique! Check ticket dataset for duplicates.")
        original_len = len(selection_cache)
        selection_cache.append(row_copy)
        new_len = len(selection_cache)
        print "[vectors] : Original dataset length: {}, new length: {}".format(original_len, new_len)

        #TODO: change prediction variable such that I can pass in a list of addon rows and get a list of predictions
        prediction = []
        generate_vectors(cfg.model_selection, selection_cache)
        cluster(cfg.model_selection, prediction)

        selection_cache.pop()
        _row_dict = {'id': row.id, 'description': row.description,
                     'system': row.system, 'ground truth': row.classification, 'prediction': ' '.join(prediction[0])}
        list_of_dicts.append(_row_dict)

    cls_path = util.generate_meta_path(cfg.model_selection, 'classifier')
    util.ensure_path_exists(cls_path)
    filename = cls_path + list_of_dicts[0]['system'] + '_classifier.csv'
    write_classifier_file(filename, list_of_dicts)
    print "[status] : Classifier finished. Analysis started."


def get_chunks(data_list):
    num_chunks = int(1 / cfg.test_dataset_split)
    len_chunk = len(data_list) / num_chunks
    remainders = len(data_list) % num_chunks
    # Chop off remainder tickets if length of data_list yields a remainder
    if remainders:
        data_list = data_list[:-remainders]
    return [data_list[i:i + len_chunk] for i in range(0, len(data_list), len_chunk)]


def setup_datasets():
    # TODO: Get in random order, sequential tickets might be similair (important when processing multiple tickets at once)
    # Create dataset stack to be labelled
    if cfg.clustering_mode == 'test':
        _dataset_stack = [row for row in DBModel.LFF_Keywords.get_db_ref_by_system(cfg.test_dataset).select()]

        if cfg.test_dataset == cfg.model_selection:
            # Split up the same dataset according to split
            chunks = get_chunks(_dataset_stack)

            # Get random index to use as test
            rand_index = random.randint(0, len(chunks) - 1)
            _dataset_stack = chunks[rand_index]
            chunks.pop(rand_index)

            # Flatten rest of chunks into selection
            selection_cache = [row for chunk in chunks for row in chunk]
            return _dataset_stack, selection_cache
        elif cfg.model_selection == 'all_systems':
            # First add all the tickets, ignoring the nested system
            selection_cache = []
            for system in util.systems:
                if system == cfg.test_dataset:
                    continue
                for row in DBModel.LFF_Keywords.get_db_ref_by_system(system):
                    selection_cache.append(row)

            # Figure out what the test dataset will be
            chunks = get_chunks(_dataset_stack)
            rand_index = random.randint(0, len(chunks) - 1)
            _dataset_stack = chunks[rand_index]
            chunks.pop(rand_index)

            # Now add the remaining tickets from the test dataset using flattened rest of chunks
            for row in [row for chunk in chunks for row in chunk]:
                selection_cache.append(row)
            return _dataset_stack, selection_cache
        else:
            selection_cache = [row for row in DBModel.LFF_Keywords.get_db_ref_by_system(cfg.model_selection).select()]
            return _dataset_stack, selection_cache
    else:
        _dataset_stack = [row for row in DBModel.LFF_Keywords.get_db_ref_by_system(cfg.labelling_dataset).select()]
        # Label dataset should never intersect with model data
        if cfg.model_selection == 'all_systems':
            selection_cache = DBModel.LFF_Keywords.select()
        else:
            selection_cache = DBModel.LFF_Keywords.get_db_ref_by_system(cfg.model_selection)
        return _dataset_stack, selection_cache


def write_classifier_file(filename, list_of_dicts):
    with open(filename, 'w') as csvfile:
        fieldnames = list_of_dicts[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_of_dicts:
            writer.writerow(row)


def uniqueness_condition(selection, addon_selection):
    original_ids = [row.id for row in selection]
    add_id = addon_selection.id

    if add_id in original_ids:
        return False
    return True
