"""

This script takes a folder of GCaMP6f angiotensin experiments and analyzes their data.
Each experiment has 1 baseline (empty) ROI and 10 true ROIs (containing neurons).
Each ROI is normalized (frame-by-frame) to the empty ROI, then baseline-subtracted to pre-drug period.
Final units are delta(F/Fa) where:
    F is the average pixel value of each ROI
    Fa is the average pixel value of the baseline ROI
    Delta represents the change from the pre-drug period

"""

import os
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt


def getExperimentTimes(path):
    times = []
    for fname in sorted(glob.glob(path+"/video/*.tif")):
        fname = os.path.basename(fname).replace(".tif", "")
        times.append(float(fname))
    times = np.array(times)
    times = times-times[0]  # baseline subtract
    times = times/60  # minutes
    return times


def plotDataLines(times, data, AVG, ERR, b1, b2, title, showLines=False, showAvg=False, saveAs=False):
    plt.figure(figsize=(8, 6))
    plt.grid(alpha=.4)
    plt.axvspan(b1, b2, color='b', alpha=.1, label="baseline")
    plt.axvspan(10, 13, color='r', alpha=.1, label="ANG-II")
    plt.axhline(0, color='k', ls='--')
    if showLines:
        for i in range(len(data[0])):
            thisData = data[:, i]
            plt.plot(times, thisData, label="ROI-%02d" % i, alpha=.8)
    if showAvg:
        plt.plot(times, AVG, color='k', lw=3, alpha=.7)
        plt.fill_between(times, AVG+ERR, AVG-ERR, color='k', alpha=.2, lw=0)
    plt.ylabel(r'$\Delta$ F/F', fontsize=16)  # delta F(neuron)/F(background)
    plt.xlabel("Experiment Duration (minutes)", fontsize=16)
    plt.title(title, fontsize=24)
    plt.legend()
    plt.tight_layout()
    plt.margins(0, .1)
    if saveAs:
        plt.savefig(saveAs)
    # plt.show()
    plt.close()


def analyzeExperiment(path, recalculate=False, baselineMinutes=[7, 9]):
    path = os.path.abspath(path)
    title = os.path.basename(path)
    print("analyzing", path)

    # create folder where output images will go
    if not os.path.exists(path+"/swhlab/"):
        os.mkdir(path+"/swhlab/")

    # figure out the timing
    #times = getExperimentTimes(path)
    framerate = 2.75  # frames per minute

    # load the data
    data = np.loadtxt(path+"/results.xls", skiprows=1, delimiter="\t")
    data = data[:, 1:]  # remove first column (just ascending numbers)
    baselineROI = data[:, 0]  # the first ROI is always a baseline
    data = data[:, 1:]  # remove the baseline column now
    times = np.arange(len(data))/framerate

    # do the analysis / ratios
    for i in range(len(data[0])):
        thisRow = data[:, i]
        thisRow = thisRow/baselineROI  # report intensity as a fraction relative to baseline
        thisRow = thisRow*100  # convert it to percent
        b1, b2 = baselineMinutes
        baseline = np.average(thisRow[int(b1*framerate):int(b2*framerate)])
        data[:, i] = thisRow - baseline

    # calculate average and stderr
    AVG = np.average(data, axis=1)
    ERR = np.std(data, axis=1)/np.sqrt(len(data))

    # save what we've calculated
    np.savetxt(path+"/dataRaw.csv", data, delimiter=',', fmt="%f")
    np.savetxt(path+"/dataAvg.csv", AVG, delimiter=',', fmt="%f")

    # create plots of what we've calculated
    plotDataLines(times, data, AVG, ERR, b1, b2, title,
                  showLines=True, saveAs=path+"/swhlab/dataLines.png")
    plotDataLines(times, data, AVG, ERR, b1, b2, title,
                  showAvg=True, saveAs=path+"/swhlab/dataAvg.png")


def makeMasterCSV(folderOfExperiments, fname):
    """combines all of a certain CSV file in each subfolder into a master CSV file ready for Origin import."""
    print(f"reading every {fname} file in {folderOfExperiments} ...")
    allData = False
    for path in sorted(os.listdir(folderOfExperiments)):
        path = os.path.join(folderOfExperiments, path)
        if not os.path.isdir(path):
            continue
        if not os.path.exists(path+"/"+fname):
            continue
        data = np.loadtxt(path+"/"+fname, delimiter=',', dtype=object)
        labelsROI = ["ROI-%02d" % (x+1) for x in range(len(data[0]))]
        labelsUnits = ["dF/F" for x in range(len(data[0]))]
        labelsLong = [os.path.basename(path)+"-"+x for x in labelsROI]
        data = np.insert(data, 0, labelsROI, axis=0)
        data = np.insert(data, 0, labelsUnits, axis=0)
        data = np.insert(data, 0, labelsLong, axis=0)
        data2 = np.empty((500, 10), dtype=object)
        data2.fill('')
        for i in range(len(data)):
            data2[i] = data[i]
        if allData is False:
            allData = data2
        else:
            allData = np.hstack((allData, data2))
    fnameOut = "ALL_"+fname
    fnameOut = os.path.join(folderOfExperiments, fnameOut)
    out = ""
    for line in allData:
        out += ",".join(line)+"\n"
    with open(fnameOut, 'w') as f:
        f.write(out)
    print("saved", fnameOut)


if __name__ == "__main__":

    # the folder to analyze is usually given as a command line argument
    if len(sys.argv) != 2:
        print("ERROR: launch with an argument (path to master experiment folder)")
        raise ValueError
    else:
        folderOfExperiments = sys.argv[1]

    # you can override that behavior here
    # folderOfExperiments = "X:\Data\AT1-Cre\MPO GCaMP6f\data"
    folderOfExperiments = os.path.abspath(folderOfExperiments)
    assert os.path.exists(folderOfExperiments)
    print("Analyzing folder of experiments:", folderOfExperiments)

    # set this if you want to forcefully re-analyze all data for the project
    recalculate = False

    # analyze folders one by one
    for path in (os.listdir(folderOfExperiments)):
        path = os.path.join(folderOfExperiments, path)
        if not os.path.isdir(path):
            continue
        if not os.path.exists(path+"/results.xls"):
            print(f"already analyzed {path}/")
            continue
        if not "animal" in path:
            continue
        if recalculate == False and os.path.exists(path+"/dataRaw.csv"):
            continue
        print(f"ANALYZING ./{path}/")
        analyzeExperiment(path, recalculate)

    # combine the raw data from each sub folder into a master CSV
    makeMasterCSV(folderOfExperiments, "dataRaw.csv")

    print("DONE")
