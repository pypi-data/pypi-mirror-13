import struct
import numpy as np

def read_int64(file_obj):
    """
    Reads an 8 byte binary integer from a file
    :param file_obj: the open file object from which to read
    :return: the eight bytes read from the file object interpreted as a long int
    """
    return struct.unpack('q', file_obj.read(8))[0]

def matload(filename):
    """
    Reads in a dense matrix from file
    :param filename: file from which to read
    :return: the matrix which has been read
    """
    f = open(filename, 'r')
    m = read_int64(f)
    n = read_int64(f)
    x = np.fromfile(f, np.dtype(np.float64), -1, "")
    x = x.reshape((m, n), order="FORTRAN")
    f.close()
    return np.mat(x)
