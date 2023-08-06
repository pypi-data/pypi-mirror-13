# Sebastian Raschka 2014-2016
# mlxtend Machine Learning Library Extensions
#
# Implementation of the logistic regression algorithm for classification.
# Author: Sebastian Raschka <sebastianraschka.com>
#
# License: BSD 3 clause

import numpy as np


class LogisticRegression(object):
    """Logistic regression classifier.

    Parameters
    ------------
    eta : float (default: 0.01)
        Learning rate (between 0.0 and 1.0)
    epochs : int (default: 50)
        Passes over the training dataset.
    learning : str (default: sgd)
        Learning rule, sgd (stochastic gradient descent)
        or gd (gradient descent).
    regularization : {None, 'l2'} (default: None)
        Type of regularization. No regularization if
        `regularization=None`.
    l2_lambda : float
        Regularization parameter for L2 regularization.
        No regularization if l2_lambda=0.0.
    shuffle : bool (default: False)
        Shuffles training data every epoch if True to prevent circles.
    random_seed : int (default: None)
        Set random state for shuffling and initializing the weights.
    zero_init_weight : bool (default: False)
        If True, weights are initialized to zero instead of small random
        numbers in the interval [-0.1, 0.1];
        ignored if solver='normal equation'

    Attributes
    -----------
    w_ : 1d-array
        Weights after fitting.

    cost_ : list
        List of floats with sum of squared error cost (sgd or gd) for every
        epoch.

    """
    def __init__(self, eta=0.01, epochs=50, regularization=None,
                 l2_lambda=0.0, learning='sgd', shuffle=False,
                 random_seed=None, zero_init_weight=False):

        np.random.seed(random_seed)
        self.eta = eta
        self.epochs = epochs
        self.l2_lambda = l2_lambda
        self.shuffle = shuffle
        self.regularization = regularization
        self.zero_init_weight = zero_init_weight

        if learning not in ('sgd', 'gd'):
            raise ValueError('learning must be sgd or gd')
        self.learning = learning

        if self.regularization not in (None, 'l2'):
            raise AttributeError('regularization must be None or "l2"')

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
            (Re)initializes weights to small random floats if True.

        Returns
        -------
        self : object

        """
        if not len(X.shape) == 2:
            raise ValueError('X must be a 2D array. Try X[:,np.newaxis]')

        if (np.unique(y) != np.array([0, 1])).all():
            raise ValueError('Supports only binary class labels 0 and 1')

        # initialize weights
        if not isinstance(init_weights, np.ndarray):
            self._init_weights(shape=1 + X.shape[1])
        else:
            self.w_ = init_weights

        self.m_ = len(self.w_)
        self.cost_ = []

        for _ in range(self.epochs):

            if self.shuffle:
                X, y = self._shuffle(X, y)

            if self.learning == 'gd':
                y_val = self.activation(X)
                errors = (y - y_val)
                neg_grad = X.T.dot(errors)
                l2_reg = self.l2_lambda * self.w_[1:]
                self.w_[1:] += self.eta * (neg_grad - l2_reg)
                self.w_[0] += self.eta * errors.sum()

            elif self.learning == 'sgd':
                for xi, yi in zip(X, y):
                    yi_val = self.activation(xi)
                    error = (yi - yi_val)
                    neg_grad = xi.dot(error)
                    l2_reg = self.l2_lambda * self.w_[1:]
                    self.w_[1:] += self.eta * (neg_grad - l2_reg)
                    self.w_[0] += self.eta * error

            self.cost_.append(self._logit_cost(y, self.activation(X)))
        return self

    def predict(self, X):
        """Predict class labels of X.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.

        Returns
        ----------
        class : int
            Predicted class label(s).

        """
        # equivalent to np.where(self.activation(X) >= 0.5, 1, 0)
        return np.where(self.net_input(X) >= 0.0, 1, 0)

    def net_input(self, X):
        """Compute the linear net input."""
        return X.dot(self.w_[1:]) + self.w_[0]

    def activation(self, X):
        """Predict class probabilities of X from the net input.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.

        Returns
        ----------
        Class 1 probability : float

        """
        z = self.net_input(X)
        return self._sigmoid(z)

    def _shuffle(self, X, y):
        """Shuffle arrays in unison."""
        r = np.random.permutation(len(y))
        return X[r], y[r]

    def _logit_cost(self, y, y_val):
        logit = -y.dot(np.log(y_val)) - ((1 - y).dot(np.log(1 - y_val)))
        if self.l2_lambda:
            l2 = self.l2_lambda / 2.0 * np.sum(self.w_[1:]**2)
            logit += l2
        return logit

    def _sigmoid(self, z):
        """Compute the output of the logistic sigmoid function."""
        return 1.0 / (1.0 + np.exp(-z))

    def _init_weights(self, shape):
        """Initialize weight coefficients of the model."""
        if self.zero_init_weight:
            self.w_ = np.zeros(shape)
        else:
            self.w_ = 0.2 * np.random.ranf(shape) - 0.5
        self.w_.astype('float64')
