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
#=====================================================================================================
import struct
import numpy
import scipy.io
import os
import scipy.sparse as sps

slash = '/'
if os.name == 'nt':
    slash = '\\'  # so this works in Windows

# exceptions for minimal data integrity checks
class Bad_directory_structure_error(Exception):
    '''Raised when a data directory specified
	does not contain subfolders named *train*, *dev*, and *test*. Any of these directories
	could be empty and the loader will hand back a :any:`DataSet` object containing no data
	which corresponds to the empty folder.'''

    pass

class Unsupported_format_error(Exception):
    '''Raised when a file with name beginning *labels_* or *features_* is encountered without one of the supported file extensions. It is okay to have other files types in your directory as long as their names don't begin with *labels_* or *features_*.'''
    pass

class Mat_format_error(Exception):
    '''Raised if the .mat file being read does not contain a
    variable named *data*.'''
    pass

class Sparse_format_error(Exception):
    '''Raised when reading a plain text file with .sparsetxt
    extension and there are not three entries per line.'''
    pass

class Mismatched_data_error(Exception):
    '''Raised if there is a mismatch in the number of rows between two matrices of a :any:`DataSet` object.
    The number of rows is the number of data points, or examples, and this loader assumes that each
    example will have each feature set and each label set. If you have missing labels or missing
    features for a particular example they may be substituted with some appropriate sentinel value.'''
    pass

class DataSet(object):
    """

    """
    def __init__(self, features, labels, num_data_points):
        self._features = features  # hashmap of feature matrices #keys are derived from what's between 'features' and file extension#in the filename
        self._labels = labels  # hashmap of label matrices  #keys are derived from what's between 'labels' and file extension #in the filename
        self._epochs_completed = 0
        self._index_in_epoch = 0
        self._num_examples = num_data_points

    @property
    def features(self):
        '''A hashmap (dictionary) of matrices from files with a *features_* prefix.
        Keys are derived from what's between *features_* and the file extension in the filename,
        e.g. the key to a matrix read from a data file named: *features_descriptor.ext*
        is the string  *'descriptor'*.'''
        return self._features
    @property
    def index_in_epoch(self):
        '''The number of datapoints that have been trained on in a particular epoch.'''
        return self._index_in_epoch
    @property
    def labels(self):
        '''A hashmap (dictionary) of matrices from files with a *labels_* prefix.
        Keys are derived from what's between *labels_* and the file extension in the filename,
        e.g. the key to a matrix read from a data file named: *labels_descriptor.ext*
        is the string  *'descriptor'*.'''
        return self._labels
    @property
    def num_examples(self):
        '''Number of rows (data points) of the matrices in this :any:`DataSet`.'''
        return self._num_examples
    @property
    def epochs_completed(self):
        '''Number of epochs the data has been used to train with.'''
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
        '''
        :param batch_size: int
        :return: A :any:`DataSet` object with the next `batch_size` examples.

        If `batch_size` is greater than the number of data points in the the data
        stream a python assert fails and the loader stops. If `batch_size`
        is greater than the number of examples left in the epoch then all the
        matrices in the data stream are shuffled and a :any:`DataSet` object containing
        the first num_examples rows of the shuffled feature matrices and label
        matrices is returned.
        '''
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

class DataSets(object):
    '''A record of DataSet objects.'''
    def __init__(self, train, dev, test):
        self._train = train
        self._dev = dev
        self._test = test

    @property
    def train(self):
        '''A :any:`DataSet` object containing matrices from the train set.'''
        return self._train
    @property
    def dev(self):
        '''A :any:`DataSet` object containing matrices from the dev set.'''
        return self._dev
    @property
    def test(self):
        '''A :any:`DataSet` object containing matrices from the test set.'''
        return self._test

def read_data_sets(directory, hashlist=None):
    '''
    :param directory: Root directory containing train, test, and dev data folders.
    :return: A :any:`DataSets` object.

    Constructs a :any:`DataSets` object from files in folder `directory`.
    '''
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
            prefix = filename.split('_')[0]
            if prefix == 'features' or prefix == 'labels':
                prefix_ = prefix +  '_'

                descriptor = (filename.split('.')[0]).split(prefix_)[-1]
                if (not hashlist) or (descriptor in hashlist):
                    dataset_map[folder][prefix][descriptor] = import_data(directory + folder + slash + filename)
                    current_num_points = dataset_map[folder][prefix][descriptor].shape[0]
                    if num_data_points == -1:
                        dataset_map[folder]['num_examples'] = current_num_points
                    if dataset_map[folder]['num_examples'] != current_num_points:
                        raise Mismatched_data_error('There are %d points in %s. '
                                                    'Other data has %d points.' %
                                                    (current_num_points, num_data_points))


    datasets = DataSets(DataSet(dataset_map['train']['features'],
                             dataset_map['train']['labels'],
                             dataset_map['train']['num_examples']),
                        DataSet(dataset_map['dev']['features'],
                           dataset_map['dev']['labels'],
                           dataset_map['dev']['num_examples']),
                        DataSet(dataset_map['test']['features'],
                            dataset_map['test']['labels'],
                            dataset_map['test']['num_examples']))
    return datasets

def import_data(filename):
    '''
    :param filename: A file of an accepted format representing a matrix.
    :return: A numpy matrix or scipy sparse csr_matrix.

    Decides how to load data into python matrices by file extension.
    Raises :any:`Unsupported_format_error` if extension is not one of the supported
    extensions (mat, sparse, binary, sparsetxt, densetxt).
    Data contained in .mat files should be saved in a matrix named *data*.
    '''
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

def center(A):
    '''
    :param A: Matrix to center about its mean.
    :return: Void (matrix is centered in place).
    '''
    if sps.isspmatrix_csr(A):
        (i,j,v) = sps.find(A)
        A = sps.csr_matrix((v - sps.csr_matrix.mean(v), (i, j)),
                           shape=(A.shape[0], A.shape[1]),
                           dtype='float32')
        return sps.csr_matrix((v - numpy.mean(v), (i, j)),
                           shape=(A.shape[0], A.shape[1]),
                           dtype='float32')
    else:
        return  A - numpy.mean(A)

def toIndex(A):
    '''
    :param A: A matrix of one hot row vectors.
    :return: The hot indices.
    '''
    return sps.find(A)[1]

def read_int64(file_obj):
    """
    :param file_obj: The open file object from which to read.
    :return: The eight bytes read from the file object interpreted as a long int.

    Reads an 8 byte binary integer from a file.
    """
    return struct.unpack('q', file_obj.read(8))[0]

def matload(filename):
    """
    :param filename: file from which to read.
    :return: the matrix which has been read.

    Reads in a dense matrix from binary file filename.
    """
    f = open(filename, 'r')
    m = read_int64(f)
    n = read_int64(f)
    x = numpy.fromfile(f, numpy.dtype(numpy.float64), -1, "")
    x = x.reshape((m, n), order="FORTRAN")
    f.close()
    return numpy.mat(x)

def smatload(filename):
    """
    :param filename: The file from which to read.
    :return: A dense matrix created from the sparse data.

    Reads in a sparse matrix from binary file.
    """
    f = open(filename, 'r')
    row = read_int64(f)
    col = read_int64(f)
    nnz = read_int64(f)
    S = numpy.fromfile(f, 'd', 3*nnz)
    f.close()
    S = S.reshape((nnz, 3))
    rows = S[:, 0].astype(int) - 1
    cols = S[:, 1].astype(int) - 1
    vals = S[:, 2]
    return sps.csr_matrix((vals, (rows, cols)), shape=(row, col))

def display(datafolder):
    '''
    :param datafolder: Root folder of matrices in .sparse, .binary, .densetxt, .sparsetxt, or .mat format
    :return: Void (Prints dimensions and hash names of matrices in dataset

    Calls :any:`read_data_sets` and prints the dimensions and keys of the feature and label matrices
    in your train, dev, and test sets.
    '''
    testDataSet = dataloader.read_data_sets(datafolder)
    #train
    print tc.colored('train:', 'yellow')
    print('%d data points' % (testDataSet.train.num_examples))
    print('features:')
    for features in testDataSet.train.features:
        print('\t %s: %s' % (features, (testDataSet.train.features[features].shape),))
    print('labels:')
    for labels in testDataSet.train.labels:
         print('\t %s: %s' % (labels, (testDataSet.train.labels[labels].shape),))

    #dev
    print tc.colored('\ndev:', 'yellow')
    print('%d data points' % (testDataSet.dev.num_examples))
    print('features:')
    for features in testDataSet.dev.features:
        print('\t %s: %s' % (features, (testDataSet.dev.features[features].shape),))
    print('labels:')
    for labels in testDataSet.dev.labels:
         print('\t %s: %s' % (labels, (testDataSet.dev.labels[labels].shape),))

    #test
    print tc.colored('\ntest:', 'yellow')
    print('%d data points' % (testDataSet.test.num_examples))
    print('features:')
    for features in testDataSet.test.features:
        print('\t %s: %s' % (features, (testDataSet.test.features[features].shape),))
    print('labels:')
    for labels in testDataSet.train.labels:
         print('\t %s: %s' % (labels, (testDataSet.dev.labels[labels].shape),))
