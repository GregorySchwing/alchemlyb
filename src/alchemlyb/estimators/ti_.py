import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator


class TI(BaseEstimator):
    """Thermodynamic integration (TI).

    Parameters
    ----------

    verbose : bool, optional
        Set to True if verbose debug output is desired.

    Attributes
    ----------

    delta_f_ : DataFrame
        The estimated dimensionless free energy difference between each state.

    d_delta_f_ : DataFrame
        The estimated statistical uncertainty (one standard deviation) in 
        dimensionless free energy differences.

    states_ : list
        Lambda states for which free energy differences were obtained.

    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def fit(self, dHdl):
        """
        Compute free energy differences between each state by integrating
        dHdl across lambda values.

        Parameters
        ----------
        dHdl : DataFrame 
            dHdl[n,k] is the potential energy gradient with respect to lambda
            for each configuration n and lambda k.

        """

        # sort by state so that rows from same state are in contiguous blocks,
        # and adjacent states are next to each other
        dHdl = dHdl.sort_index(level=dHdl.index.names[1:])

        # obtain the mean and variance of the mean for each state
        # variance calculation assumes no correlation between points
        # used to calculate mean
        means = dHdl.groupby(level=dHdl.index.names[1:]).mean()
        variances = np.square(dHdl.groupby(level=dHdl.index.names[1:]).mean())
        
        # get the lambda names
        l_types = dHdl.index.names[1:]

        # obtain vector of delta lambdas between each state
        dl = means.reset_index()[means.index.names[:]].diff().iloc[1:].values

        # apply trapezoid rule to obtain DF between each adjacent state
        deltas = (dl * (means.iloc[:-1].values + means.iloc[1:].values)/2).sum(axis=1)

        # build matrix of deltas between each state
        adelta = np.zeros((len(deltas)+1, len(deltas)+1))
        ad_delta = np.zeros_like(adelta)

        for j in range(len(deltas)):
            out = []
            dout = []
            for i in range(len(deltas) - j):
                out.append(deltas[i] + deltas[i+1:i+j+1].sum())

                # Define additional zero lambda
                a = [0.0] * len(l_types)

                # Define dl series' with additional zero lambda on the left and right
                dll = np.insert(dl[i:i + j + 1], 0, [a], axis=0)
                dlr = np.append(dl[i:i + j + 1], [a], axis=0)

                # Get a series of the form: x1, x1 + x2, ..., x(n-1) + x(n), x(n)
                dllr = dll + dlr

                # Append deviation of free energy difference between state i and i+j+1
                dout.append((dllr ** 2 * variances.iloc[i:i + j + 2].values / 4).sum(axis=1).sum())
            adelta += np.diagflat(np.array(out), k=j+1)
            ad_delta += np.diagflat(np.array(dout), k=j+1)

        # yield standard delta_f_ free energies between each state
        self.delta_f_ = pd.DataFrame(adelta - adelta.T,
                                     columns=means.index.values,
                                     index=means.index.values)

        # yield standard deviation d_delta_f_ between each state
        self.d_delta_f_ = pd.DataFrame(np.sqrt(ad_delta + ad_delta.T),
                                       columns=variances.index.values,
                                       index=variances.index.values)

        self.states_ = means.index.values.tolist()

        return self
