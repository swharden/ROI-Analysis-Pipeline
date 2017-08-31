import os
import json
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(suppress=True) # don't display scientific notation

def data_reduce(array1d,factor=1000*.3):
    newLength=int(len(array1d)/factor)
    reduced = np.empty(newLength)*np.nan
    for i in range(newLength):
        reduced[i]=np.average(array1d[factor*i:factor*(i+1)])
    return reduced

def load(fileCSV, reduceBy=300):
    print('loading data...')
    with open(fileCSV) as f:
        raw=f.read().split("\n")
    labels=raw[0].split(",") # TODO: structure array with column names
    raw=raw[1:-1] # skip first and last row
    data=np.empty((len(raw),len(labels)))*np.nan
    for row,line in enumerate(raw):
        for col,val in enumerate(line.split(",")):
            if val:
                data[row,col]=float(val)
    if reduceBy:
        print("reducing data...")
        newLength=int(len(data)/reduceBy)
        reduced = np.empty((newLength,len(labels)))*np.nan
        for i in range(len(labels)):
            reduced[:,i]=data_reduce(data[:,i],reduceBy)
        data=reduced
    notes=None
    if os.path.exists(fileCSV.replace(".csv","_notes.json")):
        with open(fileCSV.replace(".csv","_notes.json")) as f:
            notes = json.load(f)
    return labels,data,notes


if __name__=="__main__":
    print("DO NOT RUN THIS PROGRAM DIRECTLY")

    fileCSV=R"X:\Data\SCOTT\2017-08-30 GCaMP fiber photometry\2017-08-30 PFC test 1\data\slice3.csv"
    labels,data,notes=load(fileCSV)

    print('plotting...')
    plt.figure(figsize=(8,6))
    plt.grid(ls='--',alpha=.5)
    #plt.plot(data[:,0],data[:,1],label=labels[1],color='b')
    plt.plot(data[:,0],data[:,2],label=labels[2],color='g')
    #GoR = data[:,2]/data[:,1] # green over red
    #dGoR = GoR-GoR[0] # crude baseline subtraction
    #plt.plot(data[:,0],dGoR*100.0,label="green/blue")
    #plt.ylabel("delta [green / blue] (%)")
    plt.xlabel("time (seconds)")
    plt.legend()

    if notes:
        for item in notes["Timestamps"]:
            plt.axvline(item["Time"],color='r',ls='--',alpha=.5)

    plt.savefig(os.path.dirname(fileCSV)+"/test.png",dpi=300)
    plt.show()
    plt.close('all')

    #data = np.loadtxt(fileCSV,skiprows=2,delimiter=",")
