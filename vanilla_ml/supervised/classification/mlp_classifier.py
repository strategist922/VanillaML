"""
Multi-layer Perceptron (Feed-forward Neural Network)
"""
import numpy as np

from vanilla_ml.base.neural_network.activators import Sigmoid, Softmax
from vanilla_ml.base.neural_network.containers import Sequential
from vanilla_ml.base.neural_network.layers import Linear
from vanilla_ml.base.neural_network.loss import CrossEntropyLoss
from vanilla_ml.supervised.classification.abstract_classifier import AbstractClassifier
from vanilla_ml.util.metrics.accuracy import accuracy_score


class MLPClassifier(AbstractClassifier):

    def __init__(self, layers, fit_bias=False, learning_rate=1.0,
                 batch_size=10, n_epochs=50, tol=1e-5, verbose=True, random_state=42):

        assert learning_rate > 0, "Learning rate must be positive."

        # TODO: Remove fit_bias since it's already supported in layers.py
        assert not fit_bias, "fit_bias is not supported."

        self.layers = layers
        self.fit_bias = fit_bias
        self.lr = learning_rate
        self.batch_size = batch_size
        self.n_epochs = n_epochs
        self.tol = tol
        self.verbose = verbose
        self.random_state = random_state
        self._classes = None
        self.model = None

    def fit(self, X, y, sample_weights=None):
        assert sample_weights is None, "Specifying sample weights is not supported!"
        assert len(X) == len(y), "Length mismatches: len(X) = %d, len(y) = %d" % (len(X), len(y))

        np.random.seed(self.random_state)

        # if self.fit_bias:
        #     X = np.hstack((X, np.ones((X.shape[0], 1))))

        n_samples, n_features = X.shape
        self._classes = np.unique(y)
        n_classes = len(self._classes)

        # # Convert y to one-hot matrix
        # one_hot_y = misc.one_hot(y, n_classes)

        # Model
        self.model, loss = _build_model(n_features, self.layers, n_classes)

        # SGD params
        params = {"lrate": self.lr, "max_grad_norm": 40}

        indices = np.arange(n_samples)

        # Run SGD
        for epoch in range(self.n_epochs):
            if self.verbose and (epoch + 1) % 10 == 0:
                print("Epoch %d ..." % (epoch + 1))

            # For report
            total_err  = 0.
            total_cost = 0.
            total_num  = 0

            for it in range(n_samples / self.batch_size):

                # batch = np.random.choice(indices, size=self.batch_size, replace=False)
                start = it * self.batch_size
                end = min((it + 1) * self.batch_size, n_samples)
                batch = indices[start:end]
                input_data, target_data = X[batch], y[batch]

                # Forward propagation
                out = self.model.fprop(input_data)
                total_cost += loss.fprop(out, target_data)
                pred = out.argmax(axis=1)
                total_err += accuracy_score(pred, target_data)
                total_num += self.batch_size

                print("\n* Iter %d" % (it + 1))
                # print("input_data =\n%s" % input_data)
                # print("pred =\n%s" % pred)
                # print("pred_proba =\n%s" % out)
                # print("target_data =\n%s" % target_data)
                print("loss = %s" % loss.fprop(out, target_data))
                print("Accuracy = %.2f%%" % (100. * accuracy_score(target_data, pred)))

                # Backward propagation
                grad_output = loss.bprop(out, target_data)
                self.model.bprop(input_data, grad_output)
                self.model.update(params)

            # print("\n* Epoch %d" % (epoch + 1))
            # # print("%d | train error: %g" % (total_num + 1, total_err / total_num))
            # print("pred =\n%s" % pred)
            # print("target_data =\n%s" % target_data)
            # print("accuracy = %.2f%%" % (100. * accuracy_score(pred, target_data)))

    def predict_proba(self, X):
        return self.model.fprop(X)


def _build_model(input_size, layer_sizes, output_size):

    model = Sequential()
    for i in range(len(layer_sizes)):
        if i == 0:
            model.add(Linear(input_size, layer_sizes[i]))
        else:
            model.add(Linear(layer_sizes[i - 1], layer_sizes[i]))
        model.add(Sigmoid())
        # model.add(ReLU())

    model.add(Linear(layer_sizes[-1], output_size))
    model.add(Softmax(skip_bprop=True))

    # Cost
    loss = CrossEntropyLoss(size_average=True, do_softmax_bprop=True)

    return model, loss