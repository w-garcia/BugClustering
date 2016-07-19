import ConfigParser

config = ConfigParser.SafeConfigParser()

config.add_section('Topology')
config.add_section('Clustering')
config.add_section('Rendering')

config.set('Topology', 'systems_filter', 'system')
config.set('Topology', 'class_clustering_filter', 'none')
config.set('Topology', 'perform_preprocessing', 'False')
config.set('Topology', 'clustering_mode', 'test')
config.set('Topology', 'model_selection', 'zookeeper')
config.set('Topology', 'test_dataset', 'flume')
config.set('Topology', 'labelling_dataset', 'openstack')
config.set('Clustering', 'low_freq_threshold', '2')
config.set('Clustering', 'cluster_similarity_method', 'average')
config.set('Clustering', 'distance_metric', 'euclidean')
config.set('Clustering', 'weighting_scheme', 'DF')
config.set('Rendering', 'max_tree_size', '10')
config.set('Rendering', 'node_label_display', 'both')
config.set('Rendering', 'classes_of_interest', 'sw- hw- a-')
config.set('Rendering', 'draw_leaf_statistics', 'True')
config.set('Rendering', 'skip_repeated_nodes', 'True')
config.set('Rendering', 'node_cutoff_percentage', '1')

with open('options.cfg', 'wb') as cfg_file:
    config.write(cfg_file)
