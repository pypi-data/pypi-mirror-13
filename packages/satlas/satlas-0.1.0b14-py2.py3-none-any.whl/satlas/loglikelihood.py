"""
Implementation of calculation of the loglikelihood for common distributions.

.. moduleauthor:: Wouter Gins <wouter.gins@fys.kuleuven.be>
"""
import numpy as np
sqrt2pi = np.sqrt(2*np.pi)
__all__ = ['poisson_llh', 'gaussian_llh']


def poisson_llh(x, l):
    """Returns the loglikelihood for a Poisson distribution.
    In this calculation, it is assumed that the parameters
    are true, and the loglikelihood that the data is drawn from
    the distribution established by the parameters is calculated.

    Parameters
    ----------
    x : array_like
        Data that has to be tested.
    l : array_like
        Parameter for the Poisson distribution.

    Returns
    -------
    array_like
        Array with loglikelihoods for the data."""
    return x * np.log(l) - l


def gaussian_llh(x, l):
    """Returns the loglikelihood for a Gaussian distribution,
    assuming the variance is given by the square root of the fit value.
    It is assumed that the parameters are true, and the
    loglikelihood that the data is drawn from the distribution
    established by the parameters is calculated.

    Parameters
    ----------
    x : array_like
        Data that has to be tested.
    l : array_like
        Parameter for the Gaussian distrbution.

    Returns
    -------
    array_like
        Array with the loglikelihoods for the data"""
    s = l ** 0.5
    deviation = (x-l)/s
    return -(0.5 * deviation * deviation + np.log(sqrt2pi*s))

def gaussian_adapted(x, l):
    s = l ** 0.5
    deviation = (x-l)/s
    return -(0.5 * deviation * deviation)

def gaussian_traditional(x, l):
    s = x ** 0.5
    deviation = (x-l)/s
    return -(0.5 * deviation * deviation)
