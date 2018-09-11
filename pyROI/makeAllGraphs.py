"""
This script takes a folder of GCaMP6f experiments and analyzes their data.
This script is extremely rigid, and requires the folder to be organized in 
a very specific way. Image acquisition and foler arrangement is described here:
https://github.com/swharden/ROI-Analysis-Pipeline/tree/master/pyROI
"""

import os
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt

def plotDataLines(times, data, AVG, ERR, b1, b2, title, showLines=False, showAvg=False, saveAs=False):
    print(f"Creating new figure: {title}")
    plt.figure(figsize=(8, 6))
    plt.grid(alpha=.4, ls='--')
    plt.axvspan(b1, b2, color='b', alpha=.1, label="baseline", lw=0)
    #plt.axvspan(10, 13, color='r', alpha=.1, label="ANG-II", lw=0)
    plt.axhline(0, color='k', ls='--')
    if len(times)<len(data):
        print(f"There's a time point mismatch!")
        print(f"number of times seen: {len(times)}")
        print(f"number of data points: {len(data)}")
        averageTimeSpacing = times[-1]/len(times)
        print(f"average space between times: {averageTimeSpacing}")
        while len(times)<len(data):
            additionalTimePoint = times[-1]+averageTimeSpacing
            print(f"adding a time point to compensate: {additionalTimePoint}")
            times = np.append(times, additionalTimePoint)
    if showLines:
        nLines = len(data[0])
        print(f"Graphing {len(times)} time points as {nLines} individual lines")
        for i in range(nLines):
            thisData = data[:, i]
            plt.plot(times, thisData, label="ROI-%02d" % i, alpha=.8)
    if showAvg:
        print(f"Graphing {len(times)} time points as individual lines")
        plt.plot(times, AVG, color='k', lw=3, alpha=.7)
        plt.fill_between(times, AVG+ERR, AVG-ERR, color='k', alpha=.2, lw=0)
    plt.ylabel(r'$\Delta$ F/F', fontsize=16)  # delta F(neuron)/F(background)
    plt.xlabel("Experiment Duration (minutes)", fontsize=16)
    plt.title(title, fontsize=24)
    plt.legend(framealpha=1, shadow=True, fancybox=True, facecolor="#EEEEEE")
    plt.tight_layout()
    plt.margins(0, .1)
    if saveAs:
        print("saving",saveAs)
        plt.savefig(saveAs)
    plt.close()


def analyzeExperiment(path, recalculate=False, baselineMinutes=[7, 9]):
    path = os.path.abspath(path)
    title = os.path.basename(path)
    print("Analyzing experiment:", path)

    # create folder where output images will go
    if not os.path.exists(path+"/swhlab/"):
        print("making swhlab subfolder to hold output data")
        os.mkdir(path+"/swhlab/")

    # figure out the time axis
    #times = np.arange(len(data))/framerate
    times = createTimesCSVfile(path)
    avgFrameRate = len(times)/(times[-1]-times[0])

    # load the data
    data = np.loadtxt(path+"/results.xls", skiprows=1, delimiter="\t")
    data = data[:, 1:]  # remove first column (just ascending numbers)
    baselineROI = data[:, 0]  # the first ROI is always a baseline
    data = data[:, 1:]  # remove the baseline column now

    # do the analysis / ratios
    for i in range(len(data[0])):
        thisRow = data[:, i]
        thisRow = thisRow/baselineROI  # report intensity as a fraction relative to baseline
        thisRow = thisRow*100  # convert it to percent
        b1, b2 = baselineMinutes
        baseline = np.average(thisRow[int(b1*avgFrameRate):int(b2*avgFrameRate)])
        data[:, i] = thisRow - baseline

    # calculate average and stderr
    AVG = np.average(data, axis=1)
    ERR = np.std(data, axis=1)/np.power(len(data),.5)

    # save what we've calculated
    np.savetxt(path+"/dataRaw.csv", data, delimiter=',', fmt="%f")
    np.savetxt(path+"/dataAvg.csv", AVG, delimiter=',', fmt="%f")

    # create plots of what we've calculated
    plotDataLines(times, data, AVG, ERR, b1, b2, title,
                  showLines=True, saveAs=path+"/swhlab/dataLines.png")
    plotDataLines(times, data, AVG, ERR, b1, b2, title,
                  showAvg=True, saveAs=path+"/swhlab/dataAvg.png")


def makeMasterCSV(folderOfExperiments, fname="dataRaw.csv"):
    """
    combines all of a certain CSV file in each subfolder into a master CSV 
    file ready for Origin import.
    """
    print("\n\n###","Merging every dataRaw.csv into ALL_dataRaw.csv","###")
    print(f"reading every {fname} file in {folderOfExperiments} ...")
    allData = False
    print(f"loading {fname} from every experiment subfolder...")
    for path in sorted(os.listdir(folderOfExperiments)):
        path = os.path.join(folderOfExperiments, path)
        dataFile = os.path.abspath(path+"/"+fname)
        if not os.path.isdir(path):
            continue
        if not os.path.exists(dataFile):
            continue
        data = np.loadtxt(dataFile, delimiter=',', dtype=object)
        labelsROI = ["ROI-%02d" % (x+1) for x in range(len(data[0]))]
        labelsUnits = ["dF/F" for x in range(len(data[0]))]
        labelsLong = [os.path.basename(path)+"-"+x for x in labelsROI]
        data = np.insert(data, 0, labelsROI, axis=0)
        data = np.insert(data, 0, labelsUnits, axis=0)
        data = np.insert(data, 0, labelsLong, axis=0)
        data2 = np.full((500, 10), '', dtype=object)
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
        print(out, file=f)
    print("saved:", fnameOut)


def createTimesCSVfile(experimentFolder):
    videoFolder = os.path.join(experimentFolder,"video/*.tif")
    print("creating CSV of time axis from files:", videoFolder)
    files=sorted(glob.glob(videoFolder))
    files=[os.path.basename(x) for x in files]
    files=[x[:-4] for x in files if str(x).count(".")==2]
    timesSec=np.array(files,dtype=float)
    timesSec-=timesSec[0]
    timesMin=timesSec/60
    fOut = os.path.join(experimentFolder,"experiment_times_minutes.csv")
    with open(fOut,'w') as f:
        text = "\n".join(["%.03f"%x for x in timesMin])
        print(text, file=f)
    print("wrote:", fOut)
    return timesMin

def analyzeExperimentFolder(experimentFolder, recalculate=False):
    """Analyze a single GCaMP6f video experiment folder."""
    path = os.path.abspath(experimentFolder)
    print("reading contents of:",path)
    print("checking if analysis is required...",end = " ")
    if not os.path.isdir(path):
        raise ValueError(f"folder does not exist: {path}")
    if not os.path.exists(path+"/results.xls"):
        print(f"skipping (already analyzed)")
        return
    if not "animal" in path:
        print(f"skipping (word 'animal' not in filename)")
        return
    if recalculate == False and os.path.exists(path+"/dataRaw.csv"):
        print(f"skipping (dataRaw.csv exists and recalculate is set to False)")
        return
    print("it is!",path)
    analyzeExperiment(path, recalculate)

SUCCESS=R"""
               |))    |))
 .             |  )) /   ))
 \\   ^ ^      |    /      ))
  \\(((  )))   |   /        ))
   / G    )))  |  /        ))
  |o  _)   ))) | /       )))
   --' |     ))`/      )))
    ___|              )))
   / __\             ))))`()))
  /\@   /             `(())))
  \/   /  /`_______/\   \  ))))
       | |          \ \  |  )))
       | |           | | |   )))
       |_@           |_|_@    ))
      /_/           /_/_/
      """

if __name__ == "__main__":

    # require a folder path as a command line argument
    if len(sys.argv) < 2:
        print(f"ERROR: {__file__} requires an argument (folder path)")
        raise ValueError
    else:
        givenFolder = sys.argv[1]
        givenFolder = os.path.abspath(givenFolder)
    if not os.path.exists(givenFolder):
        raise ValueError(f"Folder does not exist: {givenFolder}")

    # set this if you want to forcefully re-analyze all data for the project
    if len(sys.argv)>2 and sys.argv[2].upper() == "REANALYZE":
        recalculate = True
    else:
        recalculate = False
    
    # determine if the path is an experiment folder or a folder of experiment folders
    if os.path.exists(os.path.join(givenFolder,"video")):
        print("Folder has a video/ folder")
        print("It will be analyzed as an experiment folder")
        print("\n\n### Analyzing experiment 1 of 1 ###")
        analyzeExperimentFolder(givenFolder, recalculate)
        masterFolder = os.path.dirname(givenFolder)
        makeMasterCSV(masterFolder)
    else:
        print("Folder does not have a video/ folder")
        print("It will be treated as a folder of experiment folders")
        experimentFolders=[]
        masterFolder = givenFolder
        for subFolder in os.listdir(masterFolder):
            subFolder = os.path.join(masterFolder,subFolder)
            if os.path.isdir(subFolder):
                experimentFolders.append(subFolder)
        for i,experimentFolder in enumerate(experimentFolders):
                print("\n\n### Analyzing experiment %d of %d ###"%(i+1, len(experimentFolders)))
                analyzeExperimentFolder(experimentFolder, recalculate)
        makeMasterCSV(masterFolder)    
    print(SUCCESS,"\n  Analysis completed successfully.\n\n")
