import numpy as np
import matplotlib.pyplot as plt
plt.plot(np.average(plt.imread("../../data/linescan/example/green.tif"),axis=1))
plt.savefig("output.png")