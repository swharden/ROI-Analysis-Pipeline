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
                t1_s1_1/   (*_*_* where *s time point, structure number, and scan number)
"""

import pyLineScan
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import sys

#####################################################################################################
### CODE RELATED TO COMBINING / ANALYZING CSV FILES AND DATA ########################################
#####################################################################################################

class Cell:
    def __init__(self,path):
        """this class represents a single cell's project folder (data and imaging)."""
        self.path=os.path.abspath(path)
        assert os.path.exists(self.path)
        if not os.path.exists(self.path+"/analysis/"):
            os.mkdir(self.path+"/analysis/")
        self.clearAnalysisFolder()
        self.analyzeLinescans()
        self.masterCSVs()

    def clearAnalysisFolder(self):
        print("deleting old analysis files...")
        for fname in glob.glob(self.path+"/analysis/*"):
            os.remove(fname)

    def analyzeLinescans(self,reanalyze=False):
        """run pyLineScan.LineScan() on everything in the linescans folder."""
        lsFolders = sorted(glob.glob(self.path+"/linescans/*"))
        lsFolders = [os.path.abspath(x) for x in lsFolders if os.path.isdir(x)]
        for lsFolder in lsFolders:
            if os.path.exists(lsFolder+"/analysis/data_GoR.csv") and not reanalyze:
                continue
            LS=pyLineScan.LineScan(lsFolder)
            LS.allFigures()

    def masterCSVs(self):
        """run masterCSV on every data file type."""
        for fname in ["dataG","dataR","GoR","dGoR"]:
            self.masterCSV(fname)

    def masterCSV(self,dataFname="dGoR",reanalyze=True,plotToo=True):
        """pull CSV data from several linescan folders and combine it into a master CSV."""
        fnameOut=os.path.abspath(self.path+"/analysis/linescans_%s.csv"%dataFname)
        if os.path.exists(fnameOut) and reanalyze is False:
            return
        print("creating",fnameOut)
        fnames = sorted(glob.glob(self.path+"/linescans/*"))
        data=None
        labels=[]
        for fname in fnames:
            try:
                bn=os.path.basename(fname).split("_")
                timePoint,structure,scan=bn
                csvData=np.loadtxt(fname+"/analysis/data_%s.csv"%dataFname,delimiter=',',dtype=float)
                times=csvData[:,0]
                values=csvData[:,1:]
                if data is None:
                    data=np.rot90(np.array(times,ndmin=2),k=-1) # start with the time
                    labels.append("time")
                data=np.hstack((data,values)) # then add all additional data values
                label="_".join(bn)
                for scanNumber in range(values.shape[1]): # support for multiple frames
                    labels.append(label+"_f%d"%(scanNumber+1))
            except Exception as e:
                print("not valid linescan folder:",fname)
                print(e)
        np.savetxt(fnameOut,data,fmt='%.05f',delimiter=',',header=", ".join(labels))
        if plotToo:
            MP=MasterPlot(fnameOut)
            MP.figure_averageByGroup()
            MP.figure_sweeps_overlay()
            MP.figure_sweeps_continuous()

def loadMasterCSV(fname):
    """given a maser CSV file, return [labels, data]"""
    with open(fname) as f:
        labels=f.readline()
        if labels.startswith("#"):
            labels=labels[1:]
        labels=labels.split(",")
    labels=[x.strip() for x in labels]
    data=np.loadtxt(fname,delimiter=",")
    #TODO: figure out how to have column names
    return labels,data

def labelsToGroups(labels):
    """given a list of labels, figure out how to group them ready for averaging."""
    groups={}
    for label in labels[1:]:
        timeStructure="_".join(label.split("_")[:2])
        if not timeStructure in groups:
            groups[timeStructure]=[]
        groups[timeStructure]=groups[timeStructure]+[label]
    return groups

def dataMatching(labels,data,match):
    """given labeled columns, return only columns whose label gets a match."""
    columns=[]
    for i in range(1,len(labels)):
        if match in labels[i]:
            columns.append(i)
    return data[:,columns]

def masterDataAverage(fname):
    """given a master CSV file, merge multiple timepoint-structure into AV and STDERR"""
    return



###############################################################################################################
### CODE RELATED TO MAKING GRAPHS #############################################################################
###############################################################################################################

def yAxis(fname):
    """given a fname, return a formatted Y axis label"""
    fname=os.path.basename(fname).lower()
    DELTA=r'$\Delta$'
    if "dgor" in fname:
        try:
            plt.axhline(0,color='k',ls='--',alpha=.5)
        except:
            print("couldn't draw a horizontal line, but that's okay")
        return DELTA+" G/R (%)"
    elif "gor" in fname:
        return "raw G/R (%)"
    else:
        return "???"

class MasterPlot:
    def __init__(self,fname):
        """load data from a master CSV file and plot it."""
        self.fname=os.path.abspath(fname)
        self.labels,self.data=loadMasterCSV(fname)
        self.groups=labelsToGroups(self.labels)
        self.Xs = self.data[:,0]

    def new(self):
        plt.figure(figsize=(8,6))
        plt.ylabel(yAxis(self.fname))
        plt.xlabel("time (seconds)")
        plt.title(os.path.basename(self.fname))
        plt.grid(alpha=.25,ls='--')

    def close(self,show=False,saveAs=False):
        plt.legend(fontsize=8)
        plt.margins(0,.1)
        if type(saveAs) is str:
            if not "/" in saveAs and not "\\" in saveAs:
                saveAs = self.fname+"_%s.png"%saveAs
            print('saving',os.path.basename(saveAs),'...')
            plt.savefig(saveAs,dpi=100)
        if show:
            plt.show()
        plt.close('all')

    def figure_averageByGroup(self):
        self.new()
        for i,group in enumerate(sorted(self.groups.keys())):
            #color=pyLineScan.COL(i/len(groups.keys()))
            color=pyLineScan.COLORS[i]
            thisData=dataMatching(self.labels,self.data,group)
            group+=" (n=%d)"%len(thisData[0])
            AV=np.average(thisData,axis=1)
            SD=np.std(thisData,axis=1)
            SE=SD/np.math.sqrt(len(thisData[0]))
            #plt.plot(self.Xs,thisData,color=color,alpha=.5,lw=1,ls=':')
            plt.fill_between(self.Xs,(AV-SE)*100,(AV+SE)*100,alpha=.3,color=color,lw=0)
            plt.plot(self.Xs,AV*100,color=color,alpha=.8,label=group)
        self.close(saveAs="averageByGroup")

    def figure_sweeps_overlay(self):
        self.new()
        for i in range(1,len(self.data[0])):
            color=pyLineScan.COL(i/len(self.data[0]))
            label=self.labels[i]
            plt.plot(self.Xs,self.data[:,i]*100,alpha=.8,color=color,label=label)
        self.close(saveAs="sweepsOverlay")

    def figure_sweeps_continuous(self):
        self.new()
        for i in range(1,len(self.data[0])):
            color=pyLineScan.COL(i/len(self.data[0]))
            label=self.labels[i]
            plt.plot(self.Xs+(self.Xs[-1]*i),self.data[:,i]*100,alpha=.8,color=color,label=label)
        self.close(saveAs="sweepsContinuous")

if __name__=="__main__":
    if len(sys.argv)==2:
        projectFolder=sys.argv[1]
        if os.path.exists(projectFolder):
            print("analyzing 2P linescan cell folder:\n"+projectFolder)
            Cell(projectFolder)
        else:
            print("FOLDER DOES NOT EXIST:\n"+projectFolder)
    else:
        print("DO NOT RUN THIS DIRECTLY! THIS BLOCK IS FOR DEVELOPERS/TESTING ONLY")
        #Cell(R"X:\Data\SCOTT\2017-08-28 Mannital 2P\17828_Cell1")
        #Cell(R"X:\Data\SCOTT\2017-08-28 Mannital 2P\17828_Cell2")
    print("DONE")