import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
imageData=plt.imread("../../data/linescan/example/green.tif") # load the 2D image data 
trace=np.average(imageData,axis=1) # average the image data across to create a linescan average
plt.figure(figsize=(4,4)) # make a new figure of this size in inches
plt.subplot(211) # plot in the first plot
plt.grid(alpha=.5) # add a semitransparent grid
plt.plot(trace,alpha=.5) # plot the linescan with some transparency
plt.axis('off') # hide all axis stuff
plt.subplot(212) # now move on to the second plot
plt.imshow(np.rot90(imageData), cmap='jet', aspect='auto') # plot the original data with a gray colormap
plt.axis('off') # hide all axis stuff
plt.tight_layout(0) # remove padding between subplots
plt.savefig("output_jet.png",dpi=200)