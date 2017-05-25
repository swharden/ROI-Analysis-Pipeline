import matplotlib.pyplot as plt
import numpy as np
np.set_printoptions(suppress=True) # don't show exponential notation
import os

def loadROIdata(fname, labelsToo=False):
    """
    load a CSV generated by ImageJ and return it as a numpy array.
    Returns data in the same shape as it exists in the CSV.
    """
    print("loading data from:",fname)
    with open(fname) as f:
        raw=f.readlines()
    if not raw[0].startswith(" ,"):
        for i in range(10):
            print("WARNING: This doesn't look like an ImageJ export CSV!")
    labels=raw[0].strip().split(",")
    labels[0]="frame"
    raw=raw[1:]
    nRows=len(raw)
    nCols=len(labels)
    data=np.empty((nRows,nCols))
    for row in range(nRows):
        data[row]=raw[row].split(",")
    #print(data)
    print("loaded %d lines of data from %d ROIs"%(nRows,nCols-1))
    if labelsToo:
        return [data,labels]
    return data

if __name__=="__main__":
    fldr=r"X:\Data\SCOTT\2017-05-10 GCaMP6f\2017-05-10 GCaMP6f PFC GABA cre"
    fname="2017-05-23 cell2.csv"
    data=loadROIdata(os.path.join(fldr,fname))
    print("DONE")