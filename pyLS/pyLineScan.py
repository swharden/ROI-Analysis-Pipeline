# pyLineScan is a package to aid analysis of two-photon linescans
import numpy as np
import matplotlib.pyplot as plt
import os

DELTA=r'$\Delta$'

def bilinear_interpolate(im, x, y):
    """gaussian blur for images without needing scipy"""
    x = np.asarray(x)
    y = np.asarray(y)

    x0 = np.floor(x).astype(int)
    x1 = x0 + 1
    y0 = np.floor(y).astype(int)
    y1 = y0 + 1

    x0 = np.clip(x0, 0, im.shape[1]-1);
    x1 = np.clip(x1, 0, im.shape[1]-1);
    y0 = np.clip(y0, 0, im.shape[0]-1);
    y1 = np.clip(y1, 0, im.shape[0]-1);

    Ia = im[ y0, x0 ]
    Ib = im[ y1, x0 ]
    Ic = im[ y0, x1 ]
    Id = im[ y1, x1 ]

    wa = (x1-x) * (y1-y)
    wb = (x1-x) * (y-y0)
    wc = (x-x0) * (y1-y)
    wd = (x-x0) * (y-y0)

    return wa*Ia + wb*Ib + wc*Ic + wd*Id

class LineScan:
    def __init__(self,folder,verbose=False,baseline=[.5,1.25],marks=None):
        """
        The LineScan class provides an easy object to load and analyze data from PrairieView linescan folders.
        By convension Ch1 is red (calcuim insensitive fluorophore) and Ch2 is green (calcium indicator).
        The main objects to access are green (G), red (R), and green over red (GoR).
        Baseline inputs (in seconds) are used to convert G/R to Delta(G/R)
        """

        # with out the path and name of the linescan
        self.folder=os.path.abspath(folder)
        self.verbose=verbose
        self.baselineSec=baseline
        self.marks=marks
        assert(os.path.exists(self.folder)), self.folder+" doesn't exist"
        self.name=os.path.basename(self.folder)
        if verbose: print("loading linescan",self.name)

        # figure out which files are linescans, XML data, etc
        self.files=sorted(os.listdir(self.folder))
        assert len([x for x in self.files if x.endswith(".env")]), "no .env file found"
        self.fileEnv=[x for x in self.files if x.endswith(".env")]
        assert len([x for x in self.files if x.endswith(".xml")]), "no .xml file found"
        self.fileXml=[x for x in self.files if x.endswith(".xml")][0]
        self.filesR=[x for x in self.files if x.endswith(".tif") and "_Ch1_" in x]
        self.filesG=[x for x in self.files if x.endswith(".tif") and "_Ch2_" in x]
        assert len(self.filesR)==len(self.filesG), "number of Ch1 and Ch2 tifs must match"
        if verbose: print("linescans found: %d red and %d green"%(len(self.filesR),len(self.filesG)))
        self.frames = len(self.filesR)
        self.dpi=100 # change this externally as desired

        self.confLoad() # automatically load the configuration and do the analysis
        self.dataLoad() # leaves data as 2D arrays (images)
        self.markAuto() # figure out where the brightest structure is and outline it
        self.dataFlatten() # converts data to 1D arrays (traces)

    def markAuto(self,spread=5):
        """
        Collapse the red channel in the time domain leaving only a space domain 1D array.
        Find the point of peak intensity (brightest structure).
        Set markers a certain distance on each side of the peak structure.
        """
        if not self.marks:
            self.m1,self.m2=0,self.dataG[0].shape[1]
        vertAvg=np.average(self.dataR[0],axis=0) # collapse the red channel to 1D (space domain)
        peakPos=np.where(vertAvg==max(vertAvg))[0][0]
        print("pixel row with peak intensity:",peakPos)
        self.m1,self.m2=peakPos-spread,peakPos+spread
        print("feature bounds set to %d - %d"%(self.m1,self.m2))

    def _xml_getValue(self,s):
        """return the value from an XML line ('<PVStateValue key="dwellTime" value="7.2" />' becomes 7.2)"""
        s=s.split("value=")[1].split('"')[1]
        try:return(int(s))
        except:pass
        try:return(float(s))
        except:return(s)

    def confLoad(self):
        """Load the content of the .env and .xml files to determine the parameters used to acquire the data."""
        keys=["dwellTime","scanLinePeriod","linesPerFrame","pixelsPerLine"]
        self.conf={}
        with open(os.path.join(self.folder,self.fileXml)) as f:
            for line in f.readlines():
                for key in keys:
                    if key in line:
                        self.conf[key]=self._xml_getValue(line)
                        #TODO: add code to support multiple linescan time points
        if self.verbose:
            print("CONFIGURATION:")
            for key in self.conf.keys():
                print("    "+key,"=",self.conf[key])
        self.Xs=np.arange(self.conf['linesPerFrame'])*self.conf['scanLinePeriod']
        if self.baselineSec:
            self.baselineIs=[int(self.baselineSec[0]/self.conf['scanLinePeriod']),
                             int(self.baselineSec[1]/self.conf['scanLinePeriod'])]

    def dataLoad(self):
        """load TIF data as a 2d array and store it in the lists self.dataG and self.dataR"""
        self.dataR,self.dataG,self.dataGoR=[None]*self.frames,[None]*self.frames,[None]*self.frames
        for frame in range(self.frames):
            self.dataR[frame]=plt.imread(os.path.join(self.folder,self.filesR[frame]))
            self.dataG[frame]=plt.imread(os.path.join(self.folder,self.filesG[frame]))
            self.dataGoR[frame]=self.dataG[frame]/self.dataR[frame]

    def dataFlatten(self):
        """Flatten 2d data into 1d data. Creates traceG, traceR, and traceGoR."""
        self.traceG,self.traceR,self.traceGoR=[None]*self.frames,[None]*self.frames,[None]*self.frames
        self.baselines=[None]*self.frames
        for frame in range(self.frames):
            self.traceG[frame]=np.average(self.dataG[frame][:,self.m1:self.m2],axis=1)
            self.traceR[frame]=np.average(self.dataR[frame][:,self.m1:self.m2],axis=1)
            self.traceGoR[frame]=np.average(self.dataGoR[frame][:,self.m1:self.m2],axis=1)
            if self.baselineSec:
                self.baselines[frame]=np.average(self.traceGoR[frame][self.baselineIs[0]:self.baselineIs[1]])
                self.traceGoR[frame]=self.traceGoR[frame]-self.baselines[frame]
        self.traceGoRavg=np.average(self.traceGoR,axis=0)

    def saveData(self,fname,offset=2.46872):
        header=["time"]
        data=[self.Xs+offset]
        for frame in range(self.frames):
            header.append("dGoR #%d"%(frame+1))
            data.append(self.traceGoR[frame])
        header.append("average")
        data.append(self.traceGoRavg)
        out=", ".join(header)+"\n"
        for i in range(len(data[0])):
            for j in range(len(data)):
                out+="%.05f, "%(data[j][i])
            out+="\n"
        with open(fname,'w') as f:
            f.write(out)
        print("saved",os.path.abspath(fname))

    def figureDual(self,saveAs=False):
        plt.figure(figsize=(6,10))

        ax1=plt.subplot(411)
        plt.title(self.name)
        plt.ylabel("raw pixel intensity (AFU)")
        plt.grid(alpha=.5)
        for frame in range(self.frames):
            plt.plot(self.Xs,self.traceG[frame],'-',color='G',alpha=.5)
            plt.plot(self.Xs,self.traceR[frame],'-',color='R',alpha=.5)
        plt.margins(0,.1)
        plt.axis([None,None,0,None])
        plt.setp(plt.gca().get_xticklabels(), visible=False)

        plt.subplot(412,sharex=ax1)
        title=DELTA+" [G/R] (%)"
        if self.frames>1:
            title+=" (avg n=%d)"%self.frames
        plt.ylabel(title)
        plt.grid(alpha=.5)
        plt.axhline(0,color='k',ls='--')
        print(self.baselineSec)
        if type(self.baselineSec) is list:
            plt.axvspan(self.baselineSec[0],self.baselineSec[1],alpha=.1,color='k')
        for frame in range(self.frames):
            plt.plot(self.Xs,self.traceGoRavg*100,'-',color='b',alpha=.5)
        plt.margins(0,.1)
        plt.setp(plt.gca().get_xticklabels(), visible=False)

        plt.subplot(413,sharex=ax1)
        plt.axis([None,None,0,np.shape(self.dataG)[2]])
        plt.imshow(np.rot90(np.average(self.dataG,axis=0)),cmap='gray',aspect='auto',extent=plt.axis())
        for xpos in [self.m1,self.m2]:
            plt.axhline(xpos,color='y',ls='--',lw=2)
        plt.setp(plt.gca().get_yticklabels(), visible=False)
        plt.setp(plt.gca().get_xticklabels(), visible=False)
        plt.ylabel("green channel")

        plt.subplot(414,sharex=ax1)
        plt.axis([None,None,0,np.shape(self.dataR)[2]])
        plt.imshow(np.rot90(np.average(self.dataR,axis=0)),cmap='gray',aspect='auto',extent=plt.axis())
        for xpos in [self.m1,self.m2]:
            plt.axhline(xpos,color='y',ls='--',lw=2)
        plt.setp(plt.gca().get_yticklabels(), visible=False)
        plt.ylabel("red channel")

        plt.xlabel("linescan duration (seconds)")

        plt.tight_layout()
        if saveAs:
            plt.savefig(saveAs,dpi=self.dpi)
            print("saved",os.path.abspath(saveAs))
            self.saveData(saveAs.replace(".png",".csv"))


if __name__=="__main__":
    print("DO NOT RUN THIS SCRIPT DIRECTLY")
    LS=LineScan(r'X:\Data\SCOTT\2017-06-08 2p F5 tests\2017-06-12 F4vF5 5mo rat\2p\LineScan-06122017-1612-614')
    #LS=LineScan('../data/linescan/realistic/LineScan-06092017-1414-622')
    LS.figureDual("test.png")
    plt.show()
    print("DONE")