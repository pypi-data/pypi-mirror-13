import theano
import theano.tensor as T
from theano.tensor.signal import downsample
from theano.tensor.nnet import conv
import numpy as np

class ConvLayer(object):
    """Pool Layer of a convolutional network """

    def __init__(self, rng, inputs, filter_shape, image_shape,
                #  stride, pad
                ):
        """
        Allocate a ConvPoolLayer with shared variable internal parameters.

        :type rng: numpy.random.RandomState
        :param rng: a random number generator used to initialize weights

        :type input: theano.tensor.dtensor4
        :param input: symbolic image tensor, of shape image_shape

        :type filter_shape: tuple or list of length 4
        :param filter_shape: (number of filters, num input feature maps,
                              filter height, filter width)

        :type image_shape: tuple or list of length 4
        :param image_shape: (batch size, num input feature maps,
                             image height, image width)

        :type poolsize: tuple or list of length 2
        :param poolsize: the downsampling (pooling) factor (#rows, #cols)
        """

        self.input = inputs

        self.W = theano.shared(
            np.random.normal(scale=0.1, size=filter_shape),
            borrow=True
        )

        b_values = np.zeros((filter_shape[0],), dtype=theano.config.floatX)
        self.b = theano.shared(value=b_values, borrow=True)

        # self.stride = stride
        # self.pad = pad

        conv_out = conv.conv2d(
            input=inputs,
            filters=self.W,
            image_shape=image_shape,
            filter_shape=filter_shape,
        )

        self.output = T.nnet.relu(conv_out + self.b.dimshuffle('x', 0, 'x', 'x'))

        height = image_shape[2] - filter_shape[2] + 1
        width = image_shape[3] - filter_shape[3] + 1
        self.output_shape = (image_shape[0], filter_shape[0], height, width)

        # output_shape_print = theano.printing.Print('conv layer output shape : ')(self.output_shape)

        self.params = [self.W, self.b]

        self.input = inputs

class PoolLayer(object):

    def __init__(self, inputs, input_shape, poolsize=(2,2), stride=(2,2)):
        """
        Allocate a PoolLayer.

        :type input: theano.tensor.dtensor4
        :param input: symbolic image tensor

        :type poolsize: tuple or list of length 2
        :param poolsize: the downsampling (pooling) factor (#rows, #cols)

        :type stride: tuple or list of length 2
        :param stride: the stride size (#rows, #cols)
        """

        self.input = inputs

        # downsample each feature map individually, using maxpooling
        self.output = downsample.max_pool_2d(
            input=inputs,
            ds=poolsize,
            ignore_border=True,
            # st=stride
        )

        if input_shape[2] % 2 == 0:
            height = int(input_shape[2] / 2)
        else:
            height = int((input_shape[2] - 1) / 2)

        if input_shape[3] % 2 == 0:
            width = int(input_shape[3] / 2)
        else:
            width = int((input_shape[3] - 1) / 2)

        self.output_shape = (input_shape[0], input_shape[1], height, width)

class FullyConnectedLayer(object):

    def __init__(self, inputs, n_in, n_out, rng):

        self.inputs = inputs

        self.W = theano.shared(np.random.normal(scale=0.1, size=(n_in, n_out)), borrow=True)
        self.b = theano.shared(np.random.normal(scale=0.1, size=(n_out,)), borrow=True)
        self.params = [self.W, self.b]

        self.outputs = T.nnet.relu(T.dot(self.inputs, self.W) + self.b)

class SoftmaxLayer(object):

    def __init__(self, inputs, n_in, n_out, rng):

        self.inputs = inputs

        self.W = theano.shared(np.random.normal(scale=0.1, size=(n_in, n_out)), borrow=True)
        self.b = theano.shared(np.random.normal(scale=0.1, size=(n_out,)), borrow=True)
        self.params = [self.W, self.b]

        self.p_y_given_x = T.nnet.softmax(T.dot(self.inputs, self.W)  + self.b)

        self.y_pred = T.argmax(self.p_y_given_x, axis=1)

    def negative_log_likelihood(self, y):

        return -T.mean(T.log(self.p_y_given_x)[T.arange(y.shape[0]), y])

    def errors(self, y):

        return  T.mean(T.neq(self.y_pred, y))
