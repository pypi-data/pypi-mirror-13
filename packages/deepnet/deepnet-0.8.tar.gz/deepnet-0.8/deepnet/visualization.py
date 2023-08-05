import numpy as np
import matplotlib.pyplot as plt

def init_learning_curves():

    plt.ion()
    plt.figure()
    plt.title('Learning Curves')
    plt.xlabel("Iteration")
    plt.ylabel("Error rate")

    plt.grid()

    plt.plot([], 'o-', color="r", label="Training Errors")
    plt.plot([], 'o-', color="g", label="Validation Errors")
    plt.legend(loc="best")

def update_learning_curves(i_epoch, train_error_rates, valid_error_rates):

    y_train = np.arange(len(train_error_rates))
    y_valid = np.arange(len(valid_error_rates))

    train_error_std = np.std(train_error_rates)
    valid_error_std = np.std(valid_error_rates)

    plt.fill_between(y_train, train_error_rates - train_error_std,
                     train_error_rates + train_error_std, alpha=0.1,
                     color="r")
    plt.fill_between(y_valid, valid_error_rates - valid_error_std,
                     valid_error_rates + valid_error_std, alpha=0.1, color="g")

    plt.plot(train_error_rates, 'o-', color="r", label="Training Errors")
    plt.plot(valid_error_rates, 'o-', color="g", label="Validation Errors")
    plt.pause(0.01)
