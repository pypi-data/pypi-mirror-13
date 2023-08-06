import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from sklearn.preprocessing import StandardScaler



class MTimeSeriesNnet(object):
    def __init__(self, hidden_layers = [20, 15, 5], activation_functions = ['sigmoid']*3):
        self.hidden_layers = hidden_layers
        self.activation_functions = activation_functions

        if len(self.hidden_layers) != len(self.activation_functions):
            raise Exception("hidden_layers size must match activation_functions size")

    def fit(self, multivariate_timeseries, lag = 7, epochs = 10000, verbose = 0, optimizer = 'sgd'):
        self.multivariate_timeseries = np.array(multivariate_timeseries, dtype = "float64")
        self.dimension = multivariate_timeseries.shape[1]
        self.lag = lag
        self.n = multivariate_timeseries.shape[0]
        if self.lag >= self.n:
            raise ValueError("Lag is higher than length of the timeseries")
        self.X = np.zeros((self.n - self.lag, self.lag * self.dimension), dtype = "float64")
        self.y = np.log(self.multivariate_timeseries[self.lag:,:])
        self.epochs = epochs
        self.scaler = StandardScaler()
        self.verbose = verbose
        self.optimizer = optimizer

        print "Building regressor matrix"
        # Building X matrix
        for dimension in range(self.dimension):
            for i in range(0, self.n - self.lag):
                self.X[i, (dimension * self.lag):(dimension * self.lag + self.lag)]

        print "Scaling data"
        self.scaler.fit(self.X)
        self.X  = self.scaler.transform(self.X)

        print "Checking network consistency"

        self.neural_nets = []
        for dimension in range(self.dimension):
            self.neural_nets.append(Sequential())

        for j, neural_net in enumerate(self.neural_nets):
            neural_net.add(Dense(self.X.shape[1], self.hidden_layers[0]))
            neural_net.add(Activation(self.activation_functions[0]))

            for i, layer in enumerate(self.hidden_layers[:-1]):
                neural_net.add(Dense(self.hidden_layers[i], self.hidden_layers[i + 1]))
                neural_net.add(Activation(self.activation_functions[i]))

            # Add final node
            neural_net.add(Dense(self.hidden_layers[-1],1))
            neural_net.compile(loss = 'mean_absolute_error', optimizer = self.optimizer)

            print "Training neural net number {}".format(j + 1)
            # Train neural net
            neural_net.fit(self.X, self.y[:, j], nb_epoch = self.epochs, verbose = self.verbose)

    def predict_ahead(self, n_ahead = 1):
        self.predictions = np.zeros((n_ahead, self.dimension))
        self.next_pred = np.zeros((1, self.dimension))

        for i in range(n_ahead):
            self.current_x = self.multivariate_timeseries[-self.lag:, :]
            self.current_x = self.current_x.reshape((1, self.lag * self.dimension))
            self.current_x = self.scaler.transform(self.current_x)
            # Make predictions for each time series
            for j, neural_net in enumarate(neural_nets):
                self.next_pred[j] = neural_net.predict(self.current_x)
                self.predictions[i, j] = np.exp(self.next_pred[0, 0])
            self.multivariate_timeseries = np.vstack((self.multivariate_timeseries, self.next_pred), axis = 0)

        return self.predictions
