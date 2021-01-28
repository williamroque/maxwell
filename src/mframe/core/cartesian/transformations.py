import numpy as np


class System():
    def __init__(self, scale, origin):
        self.scale = scale
        self.origin = origin

    def normalize(self, points):
        points = points * self.scale * np.array([1, -1]) + self.origin
        return points.astype(int).tolist()

    def zip_normalize(self, X, Y):
        return self.normalize(np.array(list(zip(X, Y))))
