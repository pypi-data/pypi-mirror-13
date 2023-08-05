import pickle
import os
import numpy as np
import theano.tensor as T
import theano
from theano.tensor.shared_randomstreams import RandomStreams

from .visualization import init_learning_curves, update_learning_curves
from .layers import ConvLayer, FullyConnectedLayer

class Network():

    def __init__(self, train_set_x, train_set_y, valid_set_x, valid_set_y, batch_size):

        self.train_set_x = theano.shared(np.asarray(train_set_x, dtype=theano.config.floatX),
                                      borrow=True)
        self.train_set_y = theano.shared(np.asarray(train_set_y, dtype='int32'),
                                      borrow=True)
        self.valid_set_x = theano.shared(np.asarray(valid_set_x, dtype=theano.config.floatX),
                                      borrow=True)
        self.valid_set_y = theano.shared(np.asarray(valid_set_y, dtype='int32'),
                                    borrow=True)

        self.rng = RandomStreams(seed=465)

        self.batch_size = batch_size

    def gradient_descent(self, cost, params, lr, momentum_rate):

        updates = []

        params = np.array(params).flatten()

        for param in params:

            param_update = theano.shared(param.get_value()*0., broadcastable=param.broadcastable)
            updates.append((param, param - lr*param_update))
            updates.append((param_update, momentum_rate*param_update + (1. - momentum_rate)*T.grad(cost, param)))

        return updates

    def fit(self,
              max_epoch=10,
              learning_rate=0.1, momentum_rate=0,
              weight_decay=0, lambda_1=0,
              curves = False
              ):

        self.y = T.ivector('y')
        index = T.lscalar()
        lr = T.scalar('lr')

        n_train_batch = int(self.train_set_x.get_value(borrow=True).shape[0] / self.batch_size)
        n_valid_batch = int(self.valid_set_x.get_value(borrow=True).shape[0] / self.batch_size)

        params = [layer.params for layer in self.layers if hasattr(layer, 'params')]

        # L1 = abs(self.fc1.W).sum() + abs(self.softmax_layer.W).sum()
        # L2 = (self.fc1.W**2).sum() + (self.softmax_layer.W**2).sum()
        L1 = 0
        L2 = 0
        for param in params:
            L1 += abs(param[0]).sum()
            L2 += (param[0]**2).sum()

        cost = self.layers[-1].negative_log_likelihood(self.y) + weight_decay * L2 + lambda_1 * L1

        train_model = theano.function([index, theano.Param(lr, default=learning_rate)],
                                      [cost],
                                      updates = self.gradient_descent(cost, params, lr, momentum_rate),
                                      givens = {
                                              self.x: self.train_set_x[index * self.batch_size:(index + 1) * self.batch_size],
                                              self.y: self.train_set_y[index * self.batch_size: (index + 1) * self.batch_size]
                                              }
                                     )

        train_error = theano.function( [index],
                                       [self.layers[-1].errors(self.y)],
                                       givens = {
                                            self.x: self.train_set_x[index * self.batch_size:(index + 1) * self.batch_size],
                                            self.y: self.train_set_y[index * self.batch_size: (index + 1) * self.batch_size]
                                       }
                                     )

        valid_error = theano.function( [index],
                                       [self.layers[-1].errors(self.y)],
                                       givens = {
                                            self.x: self.valid_set_x[index * self.batch_size:(index + 1) * self.batch_size],
                                            self.y: self.valid_set_y[index * self.batch_size: (index + 1) * self.batch_size]
                                       }
                                     )
        train_error_rates = []
        valid_error_rates = []
        nb_epoch = []

        nb_conv_layers = 0
        nb_fully_connected = 0
        for layer in self.layers:

            if isinstance(layer, ConvLayer):
                nb_conv_layers += 1
            elif isinstance(layer, FullyConnectedLayer):
                nb_fully_connected += 1


        print('Starting Training ...  \n')
        print('Nb Convolution Layers : %d \nNb Fully Connected Layers : %d'
              % (nb_conv_layers, nb_fully_connected) )
        print('learning rate : %f \nmomentum rate : %f \nweight_decay: %f \nlambda_1 : %f' \
              % (learning_rate, momentum_rate, weight_decay, lambda_1) )

        if curves:
            init_learning_curves()

        lr_patience_cpt = 0
        stop_patience_cpt = 0

        lr_patience = 2
        stop_patience = lr_patience*5

        improvement_threshold = 0.995

        best_validation_loss = 100
        best_epoch = 0
        for epoch in range(max_epoch):

            for iter in range(n_train_batch):

                train_model(iter, learning_rate)

            train_losses = [train_error(i) for i
                                 in range(n_train_batch)]
            valid_losses = [valid_error(i) for i
                                 in range(n_valid_batch)]

            train_loss = np.mean(train_losses)
            valid_loss = np.mean(valid_losses)
            train_error_rates.append(train_loss)
            valid_error_rates.append(valid_loss)
            nb_epoch.append(epoch)

            if curves:
                update_learning_curves(nb_epoch, train_error_rates, valid_error_rates)
            if not os.path.exists('training_outputs'):
                os.makedirs('training_outputs')
            # pickle.dump(nb_epoch, open('training_outputs/nb_epoch.p', 'wb'))
            pickle.dump(train_error_rates, open('training_outputs/train_error_rates.p', 'wb'))
            pickle.dump(valid_error_rates, open('training_outputs/valid_error_rates.p', 'wb'))

            print('epoch : %d \n train_loss : %f \n valid_loss : %f' % (epoch, train_loss, valid_loss))

            if valid_loss < best_validation_loss:
                best_validation_loss = valid_loss
                best_epoch = epoch
                if not os.path.exists('training_outputs'):
                    os.makedirs('training_outputs')
                pickle.dump(self, open('training_outputs/best_model.p', 'wb'))
                lr_patience_cpt = 0
                stop_patience_cpt = 0
            else:
                lr_patience_cpt += 1
                stop_patience_cpt += 1

            if lr_patience_cpt > lr_patience:

                learning_rate /= 2
                lr_patience_cpt = 0
                print('new learning rate : %f' % learning_rate)
            elif stop_patience_cpt > stop_patience or epoch == max_epoch:
                break

    def predict(self, test_set_x):

        test_set_x = theano.shared(np.asarray(test_set_x, dtype=theano.config.floatX),
                                      borrow=True)

        n_test_batch = int(test_set_x.get_value(borrow=True).shape[0] / self.batch_size)
        index = T.lscalar()

        predict = theano.function( [index],
                                   [self.layers[-1].y_pred],
                                   givens = {
                                        self.x: test_set_x[index * self.batch_size:(index + 1) * self.batch_size],
                                   }
                                 )

        y_pred = []
        for iter in range(n_test_batch):

            pred = predict(iter)
            y_pred.append(pred)

        return y_pred

    def features(self, test_set_x):

        test_set_x = theano.shared(np.asarray(test_set_x, dtype=theano.config.floatX),
                                      borrow=True)

        n_test_batch = int(test_set_x.get_value(borrow=True).shape[0] / self.batch_size)
        index = T.lscalar()

        features = theano.function( [index],
                                   [self.layers[-2].outputs],
                                   givens = {
                                        self.x: test_set_x[index * self.batch_size:(index + 1) * self.batch_size],
                                   }
                                 )

        all_features = None
        for iter in range(n_test_batch):

            feats = np.squeeze(features(iter))
            if all_features is None:
                all_features = feats
            else:
                all_features = np.concatenate([all_features, feats])

        return all_features
