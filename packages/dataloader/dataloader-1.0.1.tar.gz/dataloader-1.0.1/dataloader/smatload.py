import struct
import numpy as np
import scipy.sparse as sp

def read_int64(file_obj):
    """
    Reads an 8 byte binary integer from a file
    :param file_obj: the open file object from which to read
    :return: the eight bytes read from the file object interpreted as a long int
    """
    return struct.unpack('q', file_obj.read(8))[0]

def smatload(filename):
    """
    Reads in a sparse matrix from file
    :param filename: the file from which to read
    :return: a dense matrix created from the sparse data
    """
    f = open(filename, 'r')
    row = read_int64(f)
    col = read_int64(f)
    nnz = read_int64(f)
    S = np.fromfile(f,'d',3*nnz)
    f.close()
    S = S.reshape((nnz,3))
    rows = S[:,0].astype(int) - 1
    cols = S[:,1].astype(int) - 1
    vals = S[:,2]
    return sp.csr_matrix((vals, (rows, cols)), shape=(row, col))
