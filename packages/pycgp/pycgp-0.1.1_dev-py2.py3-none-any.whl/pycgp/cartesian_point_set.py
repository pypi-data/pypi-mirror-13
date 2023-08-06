import numpy as np


class CartesianPointSet():
    def __init__(self, topological_points, shape=None):
        topological_points = np.array(topological_points, np.int)
        self.cartesian_points = np.concatenate(
            (topological_points/2, (topological_points+1)/2), 0).astype(np.int)
