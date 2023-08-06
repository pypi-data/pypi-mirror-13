import h5py
import numpy as np
from scipy.sparse import csr_matrix

from .topological_point_set import TopologicalPointSet


class GeometryReader:
    def __init__(self, filename, verbose=False):
        self.geometry_file =  h5py.File(filename, 'r')
        self.verbose = verbose

        self._max_labels = self._data('max-labels')
        self._shape = self._data('segmentation-shape')
        self._part_counter = [self._data('parts-counters-%d' % (i + 1)) for i in range(3)]
        self._bounds = [self._data('neighborhood-%d' % i) for i in range(3)]

        # inverse mapping for "bounded_by" query
        self._bounded_by = [None]*4
        for cell_order in range(1,4):
            n_elements = self._max_labels[cell_order]
            bounds = self._bounds[cell_order-1]
            labels = np.arange(1, bounds.shape[1] + 1)
            labels = np.repeat(np.reshape(labels, (1, -1)), bounds.shape[0], axis=0)
            self._bounded_by[cell_order] = csr_matrix((labels.ravel(), (bounds.ravel(), labels.ravel())),
                                                      shape=(n_elements + 1, bounds.shape[1] + 1))
        # read in number-of-bins attribute
        self._n_bins = self.geometry_file.attrs['number-of-bins']


    def max_label(self, cell_order):
        return self._max_labels[cell_order]

    def size(self, cell_order, label):
        if cell_order == 0: return 1
        sizes = [self._setsdata(cell_order, label, part).shape[1]
                 for part in range(self._num_parts(cell_order, label))]
        return np.sum(sizes)

    def shape(self):
        return self._shape

    def zero_set(self, label):
        point_data = self._setsdata(0, label).T
        return TopologicalPointSet(0, point_data)

    def one_set(self, label):
        return TopologicalPointSet(1, np.abs(self._point_data(1, label)))

    def two_set(self, label):
        point_data = self._point_data(2, label)
        return TopologicalPointSet(2, np.abs(point_data), sign=np.any(point_data < 0, axis=1))

    def three_set(self, label):
        return TopologicalPointSet(3, np.abs(self._point_data(3, label)))

    def topological_point_set(self, cell_order, label):
        return TopologicalPointSet(cell_order, np.abs(self._point_data(cell_order, label)))

    def bounds(self, cell_order, label):
        if cell_order >= 3:
            raise '"cell_order" must be in {0,1,2}, but %d given' % cell_order
        neighbors = self._bounds[cell_order][:, label-1]
        return np.setdiff1d(neighbors, [0])

    def bounded_by(self, cell_order, label):
        return self._bounded_by[cell_order][label].data

    def adjacent(self, cell_order, label):
        adjacent = np.unique([adj_label for bound_label in self.bounded_by(cell_order, label)
                              for adj_label in self.bounds(cell_order - 1, bound_label)])
        return np.setdiff1d(adjacent, label)

    def _data(self, group):
        return np.array(self.geometry_file[group])

    def _setsdata(self, cell_order, label, part_number=None):
        group = '%d-sets/bin-%d/%d' % (cell_order, self._bin_number(label), label)
        if part_number is not None:
            group = '%s-%d' % (group, part_number+1)
        return np.array(self.geometry_file[group])

    def _point_data(self, cell_order, label):
        data = self._setsdata(cell_order, label, 0)
        for part in range(1, self._num_parts(cell_order, label)):
            data = np.concatenate((data, self._setsdata(cell_order, label, part)), axis=1)
        return data.T

    def _num_parts(self, cell_order, label):
        return  self._part_counter[cell_order - 1][label - 1]

    def _bin_number(self, label):
        return label % self._n_bins
