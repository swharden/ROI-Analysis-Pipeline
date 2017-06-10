import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
imageData=plt.imread("../../data/linescan/example/green.tif")
trace=np.average(imageData,axis=1)
plt.figure(figsize=(4,2))
plt.plot(trace,alpha=.5,color='y',lw=.5) # plot the data first
plt.margins(0,.1) # adjust margins so it's flush horizontally and padded vertically
plt.imshow(np.rot90(imageData), cmap='gray', aspect='auto', extent=plt.axis())
plt.axis('off') # hide all axis stuff
plt.gca().get_xaxis().set_visible(False) # remove X axis
plt.gca().get_yaxis().set_visible(False) # remove Y axis
plt.savefig("output_overlap.png",bbox_inches='tight',pad_inches=0) # extra options prevent whitespace
plt.show()
print("DONE")