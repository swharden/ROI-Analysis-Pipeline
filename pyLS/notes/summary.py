# standalone python script to generate a linescan intensity graph from a tif
import numpy as np # a helpful library for working with arrays
import matplotlib.pyplot as plt # library for graphing and working with images (may require "pillow" package)
imageData=plt.imread("../../data/linescan/example/green.tif") # load the TIF as a matrix
trace=np.average(imageData,axis=1) # average the image in the space domain (output is in the time domain)
plt.plot(trace) # create the graph
plt.savefig("output.png") # save the graph