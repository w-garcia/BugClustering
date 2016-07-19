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
        self._clustering_mode = self.config.get('Topology', 'clustering_mode')
        self._model_selection = self.config.get('Topology', 'model_selection')
        self._test_dataset = self.config.get('Topology', 'test_dataset')
        self._labelling_dataset = self.config.get('Topology', 'labelling_dataset')
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
        self._draw_trees = self.config.getboolean('Rendering', 'draw_trees')
        self._write_word_list = self.config.getboolean('Rendering', 'write_word_list')

        if self._classes_of_interest == 'all':
            self._classes_of_interest = ['a-', 'hw-', 'sw-', 'j-', 'c-', 't-', 'ht-', 'i-', 'x-']
        else:
            self._classes_of_interest = self._classes_of_interest.split(' ')

        if self._clustering_mode != 'vanilla':
            # Make sure systems filter is set to none to use all_systems as directory
            if self._model_selection == 'all' or self._model_selection == 'all_systems':
                # Force self._model_selection to 'all_systems' to be safe
                self._model_selection = 'all_systems'
                if self._systems_filter != 'none':
                    print '[warning] : All systems chosen as model, but system filter is not \'none\'.'
                    print '          : Setting systems_filter to none.'
                    self._systems_filter = 'none'
            else:
                # Opposite scenario, make sure systems filter is set to system if we only want one system in use
                if self._systems_filter != 'system':
                    print '[warning] : Single system chosen as model, but system filter is not \'system\'.'
                    print '          : Setting systems_filter to \'system\'.'
                    self._systems_filter = 'system'



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

    @property
    def clustering_mode(self):
        return self._clustering_mode

    @property
    def model_selection(self):
        return self._model_selection

    @property
    def test_dataset(self):
        return self._test_dataset

    @property
    def labelling_dataset(self):
        return self._labelling_dataset

    @property
    def draw_trees(self):
        return self._draw_trees

    @property
    def write_word_list(self):
        return self._write_word_list

    def to_file_string(self):
        topology_string = self._class_clustering_filter + '/'
        clustering_string = self._distance_metric + '-' + self._cluster_similarity_method + '/'
        scheme_string = self._weighting_scheme + '-' + str(self._low_freq_threshold) + '/'
        if self._clustering_mode == 'test':
            classifier_string = self._clustering_mode + '-' + self._model_selection + '-on-' + self._test_dataset + '/'
        elif self._clustering_mode == 'label':
            classifier_string = self._clustering_mode + '-' + self._model_selection + '-on-' + self._labelling_dataset + '/'
        else:
            classifier_string = self._clustering_mode + '/'
        return topology_string + classifier_string + clustering_string + scheme_string


config = ConfigurationManager()
