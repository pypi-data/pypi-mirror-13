# ===================================================================================================
# Aaron Tuor, Western Washington University, Jan 2016
#
# dataloader.py: General purpose dataloader for python non-sequential machine learning tasks
# Massive modification of input_data.py distributed by Google Inc.
# Original source input_data.py found at:
#
#	https://tensorflow.googlesource.com/tensorflow/+/master/tensorflow/examples/tutorials/mnist/input_data.py
#
# input_data.py is licensed under Apache License 2.0 (the "License")
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
# =====================================================================================================

import numpy
import scipy.io
import os
from matload import matload
from smatload import smatload
import scipy.sparse as sps

slash = '/'
if os.name == 'nt':
    slash = '\\'  # so this works in Windows

# exceptions for minimal data integrity checks
class Bad_directory_structure_error(Exception):
    pass

class Unsupported_format_error(Exception):
    pass

class Missing_data_error(Exception):
    pass

class Mat_format_error(Exception):
    pass

class Sparse_format_error(Exception):
    pass

class Mismatched_data_error(Exception):
    pass

''' - Classes and functions for data loader that creates a datasets object,
	containing three dataset objects.
     datasets.{train,dev,test}.{features,labels}
            - Where features is a hashmap (python dictionary) of feature matrices and labels
				is a hashmap of label matrices
            - Each feature or label matrix has first dimension (number of rows) =
                 									number of datapoints in the set
			- next_batch(k)
    Matrix Note: Each row of any data matrix corresponds to a data point in the data stream.'''

class DataSet(object):
    def __init__(self, features, labels, num_data_points):
        self._features = features  # hashmap of feature matrices #keys are derived from what's between 'features' and file extension#in the filename
        self._labels = labels  # hashmap of label matrices  #keys are derived from what's between 'labels' and file extension #in the filename
        self._labels = labels
        self._epochs_completed = 0
        self._index_in_epoch = 0
        self._num_examples = num_data_points

    @property
    def features(self):
        return self._features
    @property
    def index_in_epoch(self):
        self._index_in_epoch
    @property
    def labels(self):
        return self._labels
    @property
    def num_examples(self):
        return self._num_examples
    @property
    def epochs_completed(self):
        return self._epochs_completed

    # Underscores mean these functions are supposed to be private, but they aren't really
    def _shuffle_(self, order, datamap):
        for matrix in datamap:
            datamap[matrix] = datamap[matrix][order]

    def _next_batch_(self, datamap, start, end):
        batch_data_map = {}
        for matrix in datamap:
            batch_data_map[matrix] = datamap[matrix][start:end]
        return batch_data_map

    def next_batch(self, batch_size):
        """Return a DataSet object of the next `batch_size` examples from this data set."""
        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Shuffle the data
            perm = numpy.arange(self._num_examples)
            numpy.random.shuffle(perm)
            self._shuffle_(perm, self._features)
            self._shuffle_(perm, self._labels)
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples
        end = self._index_in_epoch
        return DataSet(self._next_batch_(self._features, start, end),
                       self._next_batch_(self._labels, start, end),
                       batch_size)

# read_data_sets: constructs DataSets object from files in folder <directory>
# <directory> structure
#		directory/{train,dev,test}/{features,labels}_{descriptor1,..,descriptorM}.{sparse,binary,mat,sparsetxt,densetxt}
#		(for non sequential data)
def read_data_sets(directory):
    if not directory.endswith(slash):
        directory += slash
    dir_files = os.listdir(directory)
    dataset_map = {'train': {'features': {}, 'labels': {}, 'num_examples': 0},  # yes a triple nested hash map
                   'test': {'features': {}, 'labels': {}, 'num_examples': 0},
                   'dev': {'features': {}, 'labels': {}, 'num_examples': 0}}
    for folder in dataset_map:  # iterates over keys
        print('reading ' + folder + '...')
        num_data_points = -1
        has_features = False
        has_labels = False
        if not folder in dir_files:
            raise Bad_directory_structure_error('Need ' + folder + ' folder in ' + directory + ' directory.')
        file_list = os.listdir(directory + folder)
        for filename in file_list:
            if filename.startswith('features'):
                descriptor = (filename.split('.')[0]).split('features_')[-1]
                dataset_map[folder]['features'][descriptor] = import_data(directory + folder + slash + filename)
                current_num_points = dataset_map[folder]['features'][descriptor].shape[0]
                if num_data_points == -1:
                    dataset_map[folder]['num_examples'] = current_num_points
                if dataset_map[folder]['num_examples'] != current_num_points:
                    raise Mismatched_data_error('There are %d points in %s. '
                                                'Other data has %d points.' %
                                                (current_num_points, num_data_points))
                has_features = True
            if filename.startswith('labels'):
                descriptor = (filename.split('.')[0]).split('labels_')[-1]
                dataset_map[folder]['labels'][descriptor] = import_data(directory + folder + slash + filename)
                has_labels = True
        if not has_features:
            raise Missing_data_error('Missing ' + folder + ' features')
        if not has_labels:
            raise Missing_data_error('Missing ' + folder + ' labels')

    class DataSets(object):  # throwaway class for packaging records
        pass

    datasets = DataSets()
    datasets.train = DataSet(dataset_map['train']['features'],
                             dataset_map['train']['labels'],
                             dataset_map['train']['num_examples'])
    datasets.dev = DataSet(dataset_map['dev']['features'],
                           dataset_map['dev']['labels'],
                           dataset_map['dev']['num_examples'])
    datasets.test = DataSet(dataset_map['test']['features'],
                            dataset_map['test']['labels'],
                            dataset_map['test']['num_examples'])
    return datasets

# import_data: Decides how to load data into python matrices by file extension
# raises Unsupported_format_error if extension is not one of the five supported
# extensions (mat, sparse, binary, sparsetxt, densetxt).
# data contained in .mat files should be saved in a matrix named 'data'
def import_data(filename):
    extension = filename.split(slash)[-1].split('.')[-1].strip()
    if extension == 'mat':
        mat_file_map = scipy.io.loadmat(filename)
        if not 'data' in mat_file_map:
            raise Mat_format_error('Matrix in .mat file ' +
                                  filename + ' must be named "data"')
        return mat_file_map['data']
    elif extension == 'sparse':
        return smatload(filename)
    elif extension == 'binary':
        return matload(filename)
    elif extension == 'sparsetxt':
        X = numpy.loadtxt(filename)
        if X.shape()[1] != 3:
            raise Sparse_format_error('Sparse Format: row col val')
        return sps.csr_matrix((X[:, 2], (X[:, 0], X[:, 1])))
    elif extension == 'densetxt':
        return numpy.loadtxt(filename)
    else:
        raise Unsupported_format_error('Supported extensions: '
                                       'mat, sparse, binary, sparsetxt, densetxt')
