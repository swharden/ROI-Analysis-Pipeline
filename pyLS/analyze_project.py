"""
Code here relates to analysis of two-photon project folders which are arranged to contain ephys (ABFs), traditional
imaging (TIFs), and two-photon imaging (linescans, single scans, t-series, and z-series) data.

PROJECT FOLDER STRUCTURE
There is a new project format. Here, each patched cell gets a parent folder:
    folderParent/          (project level parent folder)
        17828_Cell1/       (one folder per cell)
            experiment.txt (a summary of the cell)
            2P/            (contains 2P imaging: z-series, t-series, singleImage folders)
            ephys/         (contains ABFs and TIFs acquired during acquisition)
            imaging/       (contains TIFs and PNGs: non-2p imaging, IHC, etc)
            linescans/     (contains hand-renamed folders of linescan folders)
                t1_s1_1/    (*_*_* where *s time point, structure number, and scan number)
"""

import pyLineScan
import os
import glob
import numpy as np

# constants relating to linescan acquisition settings
SCAN_LINES=1000 # number of pixels wide a linescan is (time axis)
SCAN_LINE_OFFSET=2.46872 # sec offset in the ABF from the first linescan pixel
SCAN_LINE_DIFF=0.01191198 # sec spacing per line in the linsecan #TODO: WRONG

class Cell:
    def __init__(self,path):
        """this class represents a single cell's project folder (data and imaging)"""
        self.path=os.path.abspath(path)
        assert os.path.exists(self.path)
        print("\ninitiated two-photon project:",path)

        # automatic actions immediately upon loading
        if not os.path.exists(self.path+"/analysis/"):
            os.mkdir(self.path+"/analysis/")
        self.analyzeLinescans()
        self.aggregateLinescanCSVs()
        self.figureTimesAndStructures()

    def analyzeLinescans(self,reanalyze=False):
        lsFolders = sorted(glob.glob(self.path+"/linescans/*"))
        lsFolders = [os.path.abspath(x) for x in lsFolders if os.path.isdir(x)]
        for lsFolder in lsFolders:
            if os.path.exists(lsFolder+"/analysis/data_GoR.csv") and not reanalyze:
                print("skipping",lsFolder)
                continue
            print("analyzing",lsFolder)
            LS=pyLineScan.LineScan(lsFolder)
            LS.allFigures()

    def aggregateLinescanCSVs(self):
        print("aggregating linescan CSVs")
        return

    def figureTimesAndStructures(self):
        """time points and structures and scan numbers are pulled from the folder names."""
        fnames = sorted(glob.glob(self.path+"/linescans/*"))
        data=None
        labels=[]
        for fname in fnames:
            try:
                bn=os.path.basename(fname).split("_")
                timePoint,structure,scan=bn
                csvData=np.loadtxt(fname+"/analysis/data_dGoR.csv",delimiter=',',dtype=float)
                times=csvData[:,0]
                values=csvData[:,1:]
                if data is None:
                    data=np.rot90(np.array(times,ndmin=2),k=-1) # start with the time
                    labels.append("time")
                data=np.hstack((data,values)) # then add all data values
                label="_".join(bn)
                labels.append(label)
                print("incorporated",label)
            except Exception as e:
                print("not valid linescan folder:",fname)
                print(e)
        fname=os.path.abspath(self.path+"/analysis/linescans_dGoR.csv")
        np.savetxt(fname,data,fmt='%.05f',delimiter=',',header=", ".join(labels))
        print("saved",fname)
        return

if __name__=="__main__":
    print("DO NOT RUN THIS DIRECTLY! THIS IS FOR DEVELOPERS/TESTING ONLY")
    c = Cell(R"X:\Data\SCOTT\2017-08-28 Mannital 2P\17828_Cell2")

    #data=np.arange(SCAN_LINES)*SCAN_LINE_DIFF+SCAN_LINE_OFFSET

    #print(data.shape)
    #print(data)