# pyLineScan is a package to aid analysis of two-photon linescans 
import numpy as np
import matplotlib.pyplot as plt
import os

DELTA=r'$\Delta$'
    
class LineScan:
    def __init__(self,folder,verbose=False,baseline=[1.5,2.25]):
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
        self.dpi=72 # change this externally as desired

        self.confLoad() # automatically load the configuration and do the analysis
        self.dataLoad() # leaves data as 2D arrays (images)
        self.dataFlatten() # converts data to 1D arrays (traces)
        
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
        #TODO: this is where alternative trace generation methods may be used (i.e., just use brightest 10% of pixels)
        self.traceG,self.traceR,self.traceGoR=[None]*self.frames,[None]*self.frames,[None]*self.frames
        self.baselines=[None]*self.frames
        for frame in range(self.frames):
            self.traceG[frame]=np.average(self.dataG[frame],axis=1)
            self.traceR[frame]=np.average(self.dataR[frame],axis=1)
            self.traceGoR[frame]=np.average(self.dataGoR[frame],axis=1)
            if self.baselineSec:
                self.baselines[frame]=np.average(self.traceGoR[frame][self.baselineIs[0]:self.baselineIs[1]])
                self.traceGoR[frame]=self.traceGoR[frame]-self.baselines[frame]
                
    def figureRaw(self,saveAs=False):
        """generate a basic summary figure of the analyzed data."""
        plt.figure(figsize=(4,3))
        plt.title("Raw PMT Data",fontsize=16)
        plt.ylabel("raw pixel intensity (AFU)")
        plt.xlabel("linescan duration (seconds)")        
        plt.grid(alpha=.5)
        for frame in range(self.frames):
            plt.plot(self.Xs,self.traceG[frame],'-',color='G',alpha=.5)
            plt.plot(self.Xs,self.traceR[frame],'-',color='R',alpha=.5)
        plt.margins(0,.1)
        plt.axis([None,None,0,None])
        plt.tight_layout()
        if saveAs: 
            plt.savefig(saveAs,dpi=self.dpi)
                    
    def figureGoR(self,saveAs=False):
        """generate a basic summary figure of the analyzed data."""
        plt.figure(figsize=(4,3))
        plt.title("Raw PMT Data",fontsize=16)
        plt.ylabel(DELTA+"[G/R] (%)")
        plt.xlabel("linescan duration (seconds)")        
        plt.grid(alpha=.5)
        plt.axhline(0,color='k',ls='--')
        plt.axvspan(self.baselineSec[0],self.baselineSec[1],alpha=.1,color='k')
        for frame in range(self.frames):
            plt.plot(self.Xs,self.traceGoR[frame]*100,'-',color='b',alpha=.5)
        plt.margins(0,.1)
        plt.tight_layout()
        if saveAs: 
            plt.savefig(saveAs,dpi=self.dpi)
        
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
        plt.ylabel(DELTA+" [G/R] (%)")     
        plt.grid(alpha=.5)
        plt.axhline(0,color='k',ls='--')
        plt.axvspan(self.baselineSec[0],self.baselineSec[1],alpha=.1,color='k')
        for frame in range(self.frames):
            plt.plot(self.Xs,self.traceGoR[frame]*100,'-',color='b',alpha=.5)
        plt.margins(0,.1)
        plt.setp(plt.gca().get_xticklabels(), visible=False)
        
        plt.subplot(413,sharex=ax1)
        plt.imshow(np.rot90(np.average(self.dataG,axis=0)),cmap='gray',aspect='auto',extent=plt.axis())
        plt.setp(plt.gca().get_yticklabels(), visible=False)
        plt.setp(plt.gca().get_xticklabels(), visible=False)
        plt.ylabel("green channel")
        
        plt.subplot(414,sharex=ax1)
        plt.imshow(np.rot90(np.average(self.dataR,axis=0)),cmap='gray',aspect='auto',extent=plt.axis())
        plt.setp(plt.gca().get_yticklabels(), visible=False)
        plt.ylabel("red channel")
        
        plt.xlabel("linescan duration (seconds)")   
        
        plt.tight_layout()     
        if saveAs: 
            plt.savefig(saveAs,dpi=self.dpi)

if __name__=="__main__":
    print("DO NOT RUN THIS SCRIPT DIRECTLY")
#    LS=LineScan('../data/linescan/realistic/LineScan-06092017-1414-622')
#    LS.figureRaw("output_raw.png")
#    LS.figureGoR("output_dGoR.png")
#    LS.figureDual("output_dual.png")
#    plt.show()
#    print("DONE")