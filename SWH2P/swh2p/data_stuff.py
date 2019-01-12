import numpy as np

def convolve(signal,kernel):
    """
    This applies a kernel to a signal through convolution and returns the result.

    Some magic is done at the edges so the result doesn't apprach zero:
        1. extend the signal's edges with len(kernel)/2 duplicated values
        2. perform the convolution ('same' mode)
        3. slice-off the ends we added
        4. return the same number of points as the original
    """
    pad=np.ones(len(kernel)/2)
    signal=np.concatenate((pad*signal[0],signal,pad*signal[-1]))
    signal=np.convolve(signal,kernel,mode='same')
    signal=signal[len(pad):-len(pad)]
    return signal

def kernel_gaussian(size=100, sigma=None, forwardOnly=False):
    """
    return a 1d gassuan array of a given size and sigma.
    If sigma isn't given, it will be 1/10 of the size, which is usually good.
    Note that this is fully numpy, and doesn't use scipy.
    """
    if sigma is None:
        sigma=size/10
    size=int(size)
    points=np.exp(-np.power(np.arange(size)-size/2,2)/(2*np.power(sigma,2)))
    if forwardOnly:
        points[:int(len(points)/2)]=0
    return points/sum(points)

def lowpass(data,filterSize=None):
    """
    minimal complexity low-pass filtering.
    Filter size is how "wide" the filter will be.
    Sigma will be 1/10 of this filter width.
    If filter size isn't given, it will be 1/10 of the data size.
    """
    if filterSize is None:
        filterSize=len(data)/10
    kernel=kernel_gaussian(size=filterSize)
    data=convolve(data,kernel) # do the convolution with padded edges
    return data