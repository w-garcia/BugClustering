import os
import ConfigParser


class ConfigurationManager:
    def __init__(self):
        """
        config.set('Topology', 'systems_filter', 'none')
        config.set('Topology', 'class_clustering_filter', 'none')
        config.set('Topology', 'perform_preprocessing,' 'false')

        config.set('Clustering', 'low_freq_threshold', '2')
        config.set('Clustering', 'cluster_similarity_method', 'average')
        config.set('Clustering', 'distance_metric', 'euclidean')

        config.set('Rendering', 'max_tree_size', '50')
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

    def to_file_string(self):
        topology_string = self._class_clustering_filter + '/'
        clustering_string = self._distance_metric + '-' + self._cluster_similarity_method + '/'
        scheme_string = self._weighting_scheme + '-' + str(self._low_freq_threshold) + '/'
        return topology_string + clustering_string + scheme_string


config = ConfigurationManager()
