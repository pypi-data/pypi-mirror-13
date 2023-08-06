# Sebastian Raschka 2014-2016
# mlxtend Machine Learning Library Extensions
#
# Implementation of Rosenblatt's perceptron algorithm for classification.
# Author: Sebastian Raschka <sebastianraschka.com>
#
# License: BSD 3 clause

import numpy as np


class Perceptron(object):
    """Perceptron classifier.

    Parameters
    ------------
    eta : float (default: 0.1)
        Learning rate (between 0.0 and 1.0)
    epochs : int (default: 50)
        Number of passes over the training dataset.
    shuffle : bool (default: False)
         Shuffles training data every epoch if True to prevent circles.
    random_seed : int
        Random state for initializing random weights.
    zero_init_weight : bool (default: False)
        If True, weights are initialized to zero instead of small random
        numbers in the interval [-0.1, 0.1];
        ignored if solver='normal equation'

    Attributes
    -----------
    w_ : 1d-array
        Weights after fitting.
    cost_ : list
        Number of misclassifications in every epoch.

    """
    def __init__(self, eta=0.1, epochs=50, shuffle=False,
                 random_seed=None, zero_init_weight=False):

        np.random.seed(random_seed)
        self.eta = eta
        self.epochs = epochs
        self.shuffle = shuffle
        self.zero_init_weight = zero_init_weight

    def fit(self, X, y, init_weights=True):
        """Learn weight coefficients from training data.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.
        y : array-like, shape = [n_samples]
            Target values.
        init_weights : bool (default: True)
            Re-initializes weights prior to fitting. Set False to continue
            training with weights from a previous fitting.

        Returns
        -------
        self

        """
        # check array shape
        if not len(X.shape) == 2:
            raise ValueError('X must be a 2D array. Try X[:,np.newaxis]')

        # check if {0, 1} or {-1, 1} class labels are used
        self.classes_ = np.unique(y)
        if not (np.all(np.array([0, 1]) == self.classes_) or
                np.all(np.array([-1, 1]) == self.classes_)):
            raise ValueError('Only supports binary'
                             ' class labels {0, 1} or {-1, 1}.')

        if init_weights:
            self._init_weights(shape=X.shape[1]+1)
            print(self.w_)

        self.cost_ = []

        # learn weights
        for _ in range(self.epochs):
            if self.shuffle:
                X, y = self._shuffle(X, y)
            errors = 0
            for xi, target in zip(X, y):
                update = self.eta * (target - self.predict(xi))
                self.w_[1:] += update * xi
                self.w_[0] += update
                errors += int(update != 0.0)

            self.cost_.append(errors)
        return self

    def _init_weights(self, shape):
        """Initialize weights"""
        if self.zero_init_weight:
            self.w_ = np.zeros(shape)
        else:
            self.w_ = 0.2 * np.random.ranf(shape) - 0.5
        self.w_.astype('float64')

    def _shuffle(self, X, y):
        """Shuffle arrays in unison."""
        r = np.random.permutation(len(y))
        return X[r], y[r]

    def net_input(self, X):
        """ Net input function """
        return np.dot(X, self.w_[1:]) + self.w_[0]

    def predict(self, X):
        """ Predict class labels for X.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.

        Returns
        ----------
        class : int
          Predicted class label.

        """
        return np.where(self.net_input(X) >= 0.0,
                        self.classes_[1], self.classes_[0])
