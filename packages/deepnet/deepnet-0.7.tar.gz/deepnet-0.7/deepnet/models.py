import numpy as np
import theano
import theano.tensor as T
import sys

from .layers import FullyConnectedLayer, SoftmaxLayer, PoolLayer, ConvLayer
from .net import Network

class ConvNet(Network):

    def __init__(self, train_set_x, train_set_y, valid_set_x, valid_set_y, batch_size, nkerns=[20, 50], nb_neurons=[225, 100]):

        if sys.version_info < (3,0):
            Network.__init__(self, train_set_x, train_set_y, valid_set_x, valid_set_y, batch_size)
        else:
            super().__init__(train_set_x, train_set_y, valid_set_x, valid_set_y, batch_size)

        self.x = T.dtensor4('x')

        nb_channel = train_set_x.shape[1]
        height = train_set_x.shape[2]
        width = train_set_x.shape[3]

        self.layers = []

        layer0 = ConvLayer(
            self.rng,
            inputs=self.x,
            image_shape=(batch_size, nb_channel, height, width),
            filter_shape=(nkerns[0], nb_channel, 6, 6),
         #    stride=2,
         #    pad=2
        )

        layer1 = PoolLayer(
            inputs=layer0.output,
            input_shape=layer0.output_shape
        )

        self.layers.append(layer0)
        self.layers.append(layer1)

        # nkerns.pop(0)
        for i, layer_param in enumerate(nkerns):

            if i != 0:
                layer = ConvLayer(
                    self.rng,
                    inputs=self.layers[-1].output,
                    image_shape=self.layers[-1].output_shape,
                    filter_shape=(nkerns[i], nkerns[i-1], 6, 6),
                 #    stride=2,
                 #    pad=2
                )

                self.layers.append(layer)

                layer = PoolLayer(
                    inputs=self.layers[-1].output,
                    input_shape=self.layers[-1].output_shape
                )

                self.layers.append(layer)

        layer4_input = self.layers[-1].output.flatten(2)

        n_in = self.layers[-1].output_shape[1] * self.layers[-1].output_shape[2] * self.layers[-1].output_shape[3]
        # n_out = int(n_in/2)

        layer = FullyConnectedLayer(layer4_input, n_in, nb_neurons[0], self.rng)

        self.layers.append(layer)

        n_in = nb_neurons[0]
        nb_neurons.pop(0)
        for n_out in nb_neurons:

            inputs = self.layers[-1].outputs
            layer = FullyConnectedLayer(inputs, n_in, n_out, self.rng)
            n_in = n_out
            self.layers.append(layer)

        nb_outputs = len(np.unique(train_set_y))
        layer = SoftmaxLayer(inputs=self.layers[-1].outputs, n_in=n_out, n_out=nb_outputs, rng=self.rng)

        self.layers.append(layer)

class MLP(Network):

    def __init__(self, train_set_x, train_set_y, valid_set_x, valid_set_y, batch_size, nb_neurons=[]):

        if sys.version_info < (3,0):
            Network.__init__(self, train_set_x, train_set_y, valid_set_x, valid_set_y, batch_size)
        else:
            super().__init__(train_set_x, train_set_y, valid_set_x, valid_set_y, batch_size)

        self.x = T.dmatrix('x')

        nb_features = self.train_set_x.get_value().shape[1]
        fc1 = FullyConnectedLayer(self.x, nb_features, nb_features, self.rng)

        self.layers = []
        self.layers.append(fc1)
        n_in = nb_features
        for n_out in nb_neurons:

            inputs = self.layers[-1].outputs
            layer = FullyConnectedLayer(inputs, n_in, n_out, self.rng)
            n_in = n_out
            self.layers.append(layer)

        n_out = len(np.unique(self.train_set_y.get_value()))
        if len(hidden_layers) != 0:
            n_in = hidden_layers[-1]
        else:
            n_in = nb_features

        softmax_layer = SoftmaxLayer(self.layers[-1].outputs, n_in, n_out, self.rng)
        self.layers.append(softmax_layer)
