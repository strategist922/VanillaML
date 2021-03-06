"""
Misc utility
"""
from __future__ import division

import os
from os import path
import itertools
import urllib

import numpy as np


def download_file(url, local_path):
    dir_path = path.dirname(local_path)
    if not path.exists(dir_path):
        print("Creating the directory '%s' ..." % dir_path)
        os.makedirs(dir_path)

    urllib.URLopener().retrieve(url, local_path)


def sigmoid(x):
    return 1. / (1 + np.exp(-x))


def sign(x):
    return 1 if x >= 0 else -1


def get_penalty(w, factor, penalty):
    """ Get penalty for the input ndarray.

    Args:
        w (ndarray): input data, shape K x P
        factor (float): penalty factor
        penalty (str): penalty type

    Returns:
        ndarray: penalty values

    """
    assert factor > 0, "The penalty factor must be positive."

    if penalty == 'l1':
        raise Exception("L1 penalty is not supported yet!")
    elif penalty == 'l2':
        return 2 * factor * w
    else:
        raise Exception("The penalty '%s' is not supported!" % penalty)


def label_to_sign(y):
    """
    Maps {0, 1} to {-1, 1}.
    """
    return 2 * y - 1


def sign_to_label(y):
    """
    Maps {-1, 1} to {0, 1}.
    """
    return (y + 1) / 2


def one_hot(y, n_classes=None):
    """ Convert an 1D array to one-hot 2D array (using one-liner trick).

    Args:
        y (ndarray): uint array, shape N
        n_classes (Optional[int]): number of classes.

    Returns:
        ndarray: one-hot 2D array, shape N x K

    """
    if n_classes is None:
        n_classes = len(np.unique(y))
    return np.eye(n_classes)[y]


def softmax(X):
    """ Compute softmax (based on the formulas 3.70 and 8.33 in Kevin Murphy's book).

    Args:
        X (ndarray): array, shape N x K

    Returns:
        ndarray: softmax, shape N x 1.

    """
    log_sum_exp_X = log_sum_exp(X)
    return np.exp(X - log_sum_exp_X[:, None])


def log_sum_exp(X):
    """ Compute log of sum of exps.
    Using the log-sum-exp trick as shown in the formula 3.74 in Kevin Murphy's book.

    Args:
        X (ndarray): array, shape N x K

    Returns:
        ndarray: log-sum-exp results, shape N x 1.

    """
    max_X = X.max(axis=1)
    return max_X + np.log(np.sum(np.exp(X - max_X[:, None]), axis=1))


def train_test_split(X, y, test_size=0.25, random_state=42):
    """ Split the data set into training and test sets.

    Args:
        X (ndarray): data
        y (ndarray): target
        test_size (float): percentage of the test set
        random_state (int): random state

    Returns:
        tuple: a tuple of X_train, X_test, y_train, y_test

    """
    assert X.shape[0] == y.shape[0], "X, y have mismatched lengths"
    orig_size = X.shape[0]
    train_size = int(orig_size * (1 - test_size))
    np.random.seed(random_state)
    rand_indices = np.random.permutation(orig_size)
    train_indices, test_indices = \
        rand_indices[:train_size], rand_indices[train_size:]

    return X[train_indices], X[test_indices], \
           y[train_indices], y[test_indices]


# Adapted from sklearn's make_moons()
def make_moons(n_samples, noise=0.3, random_state=42):
    """ Generate two moons.

    Args:
        n_samples (int): number of samples to generate
        noise (float): noise level
        random_state (int): random state

    Returns:
        tuple: a tuple of X and y

    """
    np.random.seed(random_state)

    n_samples_out = n_samples // 2
    n_samples_in = n_samples - n_samples_out

    outer_circ_x = np.cos(np.linspace(0, np.pi, n_samples_out))
    outer_circ_y = np.sin(np.linspace(0, np.pi, n_samples_out))
    inner_circ_x = 1 - np.cos(np.linspace(0, np.pi, n_samples_in))
    inner_circ_y = 1 - np.sin(np.linspace(0, np.pi, n_samples_in)) - .5

    X = np.vstack((np.append(outer_circ_x, inner_circ_x),
                   np.append(outer_circ_y, inner_circ_y))).T
    y = np.hstack([np.zeros(n_samples_in, dtype=np.intp),
                   np.ones(n_samples_out, dtype=np.intp)])

    # Add noise
    X += np.random.normal(scale=noise, size=X.shape)

    # Shuffle
    shuffled_indices = np.random.permutation(n_samples)
    return X[shuffled_indices], y[shuffled_indices]


# Adapted from sklearn's make_blobs
def make_blobs(n_samples=100, n_features=2, n_centers=3, centers=None, cluster_std=1.0,
               center_range=(-10.0, 10.0), random_state=None):
    """ Draw random data from Gaussian for clustering.

    Args:
        n_samples (int): number of samples to generate.
        n_features (int): number of features, i.e. data point's dimensions.
        n_centers (int): number of clusters
        centers (Optional[ndarray]): an array of shape [n_centers, n_features]
                                    for center locations.
        cluster_std (float): cluster's standard deviation.
        center_range (tuple): a tuple of min and max values of cluster centers.
        random_state (int): random state.

    Returns:
        tuple: a tuple of data and target.

    """
    np.random.seed(random_state)

    # Generate random cluster centers if they are not given
    if centers is None:
        center_low, center_high = center_range
        centers = np.random.uniform(center_low, center_high,
                                    size=(centers, n_features))
    else:
        n_centers, n_features = centers.shape

    # Calculate number of samples per center
    n_samples_per_center = [int(n_samples // n_centers)] * n_centers
    for i in range(n_samples % n_centers):
        n_samples_per_center[i] += 1

    # Generate blobs
    X, y = [], []
    for i, n in enumerate(n_samples_per_center):
        X.append(centers[i] + np.random.normal(scale=cluster_std, size=(n, n_features)))
        y += [i] * n

    X = np.concatenate(X)
    y = np.array(y)
    rand_indices = np.random.permutation(n_samples)
    return X[rand_indices], y[rand_indices]


# TODO: Move this to PairwiseTransformer
def pairwise_transform(X, y=None):
    """ Pairwise transformation.

    Args:
        X (ndarray): data points, shape (N, ) or (N, 2).
            If the shape is (N, 2), the second column represents data point's group.
        y (Optional[ndarray]): ranking labels, shape (N, ).

    Returns:
        tuple: a tuple (X_diff, y_diff)
            where X_diff contains pairwise differences of X
            and y_diff contains -1 and 1 indicating ranking of datapoints in X.

    """
    assert X.shape[0] == y.shape[0], "X, y have mismatched lengths."

    N = X.shape[0]
    y = np.asarray(y) if y is not None else np.arange(N)

    X_diff, y_diff = [], []

    for i, j in itertools.combinations(range(N), 2):
        # Skip the pair of data points that have the same ranks
        if y[i] == y[j]:
            continue
        X_diff.append(X[i] - X[j])
        y_diff.append(np.sign(y[i] - y[j]))

    return np.asarray(X_diff), np.asarray(y_diff)
