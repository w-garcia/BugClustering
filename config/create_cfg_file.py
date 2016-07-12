import ConfigParser

config = ConfigParser.SafeConfigParser()

config.add_section('Topology')
config.add_section('Clustering')
config.add_section('Rendering')

config.set('Topology', 'systems_filter', 'system')
config.set('Topology', 'class_clustering_filter', 'sw-')
config.set('Topology', 'perform_preprocessing', 'False')
config.set('Clustering', 'low_freq_threshold', '2')
config.set('Clustering', 'cluster_similarity_method', 'average')
config.set('Clustering', 'distance_metric', 'cosine')
config.set('Clustering', 'weighting_scheme', 'DF')
config.set('Rendering', 'max_tree_size', '50')

with open('options.cfg', 'wb') as cfg_file:
    config.write(cfg_file)
