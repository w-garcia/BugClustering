import ConfigParser

config = ConfigParser.SafeConfigParser()

config.add_section('Topology')
config.add_section('Clustering')
config.add_section('Rendering')

config.set('Topology', 'systems_filter', 'system')
config.set('Topology', 'class_clustering_filter', 'none')
config.set('Topology', 'perform_preprocessing', 'False')
config.set('Topology', 'clustering_mode', 'vanilla')
config.set('Topology', 'model_selection', 'zookeeper')
config.set('Topology', 'test_dataset', 'zookeeper')
config.set('Topology', 'test_dataset_split', '0.1')
config.set('Topology', 'labelling_dataset', 'openstack')
config.set('Topology', 'cross_validation_mode', 'kfold')
config.set('Topology', 'retrieve_label_datasets', 'True')
config.set('Clustering', 'low_freq_threshold', '2')
config.set('Clustering', 'cluster_similarity_method', 'average')
config.set('Clustering', 'distance_metric', 'euclidean')
config.set('Clustering', 'weighting_scheme', 'TF')
config.set('Rendering', 'max_tree_size', '50')
config.set('Rendering', 'node_label_display', 'both')
config.set('Rendering', 'classes_of_interest', 'a- sw- hw-')
config.set('Rendering', 'draw_leaf_statistics', 'True')
config.set('Rendering', 'skip_repeated_nodes', 'True')
config.set('Rendering', 'node_cutoff_percentage', '1')
config.set('Rendering', 'draw_trees', 'False')
config.set('Rendering', 'write_word_list', 'False')

with open('options.cfg', 'wb') as cfg_file:
    config.write(cfg_file)
