import os
import ConfigParser


class ConfigurationManager:
    def __init__(self):
        """
        Manages the configuration.
        :return:
        """
        self.config = ConfigParser.SafeConfigParser()
        config_path = os.getcwd() + '/config/options.cfg'
        self.config.read(config_path)
        self._systems_filter = self.config.get('Topology', 'systems_filter')
        self._class_clustering_filter = self.config.get('Topology', 'class_clustering_filter')
        self._perform_preprocessing = self.config.getboolean('Topology', 'perform_preprocessing')
        self._low_freq_threshold = self.config.getint('Clustering', 'low_freq_threshold')
        self._cluster_similarity_method = self.config.get('Clustering', 'cluster_similarity_method')
        self._distance_metric = self.config.get('Clustering', 'distance_metric')
        self._weighting_scheme = self.config.get('Clustering', 'weighting_scheme')
        self._max_tree_size = self.config.getint('Rendering', 'max_tree_size')
        self._node_label_display = self.config.get('Rendering', 'node_label_display')
        self._classes_of_interest = self.config.get('Rendering', 'classes_of_interest')
        self._draw_leaf_statistics = self.config.getboolean('Rendering', 'draw_leaf_statistics')
        self._skip_repeated_nodes = self.config.getboolean('Rendering', 'skip_repeated_nodes')
        self._node_cutoff_percentage = self.config.getfloat('Rendering', 'node_cutoff_percentage')

        if self._classes_of_interest == 'all':
            self._classes_of_interest = ['a-', 'hw-', 'sw-', 'j-', 'c-', 't-', 'ht-', 'i-', 'x-']
        else:
            self._classes_of_interest = self._classes_of_interest.split(' ')

    @property
    def systems_filter(self):
        return self._systems_filter

    @property
    def class_clustering_filter(self):
        return self._class_clustering_filter

    @property
    def perform_preprocessing(self):
        return self._perform_preprocessing

    @property
    def low_freq_threshold(self):
        return self._low_freq_threshold

    @property
    def cluster_similarity_method(self):
        return self._cluster_similarity_method

    @property
    def distance_metric(self):
        return self._distance_metric

    @property
    def weighting_scheme(self):
        return self._weighting_scheme

    @property
    def max_tree_size(self):
        return self._max_tree_size

    @property
    def node_label_display(self):
        return self._node_label_display

    @property
    def classes_of_interest(self):
        return self._classes_of_interest

    @property
    def draw_leaf_statistics(self):
        return self._draw_leaf_statistics

    @property
    def skip_repeated_nodes(self):
        return self._skip_repeated_nodes

    @property
    def node_cutoff_percentage(self):
        return self._node_cutoff_percentage

    def to_file_string(self):
        topology_string = self._class_clustering_filter + '/'
        clustering_string = self._distance_metric + '-' + self._cluster_similarity_method + '/'
        scheme_string = self._weighting_scheme + '-' + str(self._low_freq_threshold) + '/'
        return topology_string + clustering_string + scheme_string


config = ConfigurationManager()
