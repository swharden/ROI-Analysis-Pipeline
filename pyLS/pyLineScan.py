# pyLineScan is a package to aid analysis of two-photon linescans
import numpy as np
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
import os
import glob
import datetime
from PIL import Image
from PIL import ImageEnhance
import webbrowser
import sys

DELTA=r'$\Delta$'

class LineScan:
    def __init__(self,folder,verbose=False,baseline=None,marks=None,sigma=5):
        """
        The LineScan class provides an easy object to load and analyze data from PrairieView linescan folders.
        By convension Ch1 is red (calcuim insensitive fluorophore) and Ch2 is green (calcium indicator).
        The main objects to access are green (G), red (R), and green over red (GoR).
        Baseline inputs (in seconds) are used to convert G/R to Delta(G/R)
        """

        # with out the path and name of the linescan
        self.folder=os.path.abspath(folder)
        self.folderOut=os.path.abspath(os.path.join(self.folder,"analysis/"))
        print("\n\nLOADING [%s]\n%s"%(os.path.basename(self.folder),self.folder))
        if not os.path.exists(self.folderOut):
            os.mkdir(self.folderOut)
        self.verbose=verbose
        self.baselineSec=baseline
        self.marks=marks
        self.sigma=sigma
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

        ### do these things automatically when the class is loaded
        self.confLoad() # load the configuration
        self.dataLoad() # load image data as 2D arrays
        self.markAuto() # figure out where the brightest structure is and outline it
        self.dataFlatten() # converts data to 1D arrays (traces) and handle baseline subtraction

    def markAuto(self,spread=5):
        """
        Collapse the red channel in the time domain leaving only a space domain 1D array.
        Find the point of peak intensity (brightest structure).
        Set markers a certain distance on each side of the peak structure.
        """
        if not self.marks:
            self.m1,self.m2=0,self.dataG[0].shape[1]
        vertAvg=np.average(np.average(self.dataR,axis=0),axis=0) # collapse the red channel to 1D (space domain)
        maxValue=max(vertAvg)
        minValue=min(vertAvg)
        cutoff=(maxValue-minValue)*.25+minValue # bottom 25%
        peakPos=np.where(vertAvg==maxValue)[0][0]
        print("pixel row with peak intensity:",peakPos)
        self.m1,self.m2=peakPos,peakPos
        for y in range(peakPos,len(vertAvg)):
            if vertAvg[y]>cutoff:self.m2=y+2
            else:break
        for y in range(peakPos,0,-1):
            if vertAvg[y]>cutoff:self.m1=y
            else:break
        print("marks automatically set to %d - %d"%(self.m1,self.m2))

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
        else:
            self.baselineIs=[int(len(self.Xs)*.05),int(len(self.Xs)*.15)] # default to first 5-15% of the window
            self.baselineSec=[self.Xs[self.baselineIs[0]],self.Xs[self.baselineIs[1]]]

    def dataLoad(self):
        """load TIF data as a 2d array and store it in the lists self.dataG and self.dataR"""
        self.dataR,self.dataG,self.dataGoR=[None]*self.frames,[None]*self.frames,[None]*self.frames
        for frame in range(self.frames):
            print("  loading frame %d of %d ..."%(frame+1,self.frames))
            self.dataR[frame]=plt.imread(os.path.join(self.folder,self.filesR[frame]))
            self.dataG[frame]=plt.imread(os.path.join(self.folder,self.filesG[frame]))
            if self.sigma>1:
                # gaussian smoothing of image in the time domain
                self.dataR[frame]=ndimage.gaussian_filter(self.dataR[frame],sigma=(self.sigma,0))
                self.dataG[frame]=ndimage.gaussian_filter(self.dataG[frame],sigma=(self.sigma,0))
            self.dataGoR[frame]=self.dataG[frame]/self.dataR[frame]

    def dataFlatten(self):
        """Flatten 2d data into 1d data. Creates traceG, traceR, and traceGoR."""
        self.traceG=np.array([None]*self.frames)
        self.traceR=np.array([None]*self.frames)
        self.traceGoR=np.array([None]*self.frames)
        self.dGoR=np.array([None]*self.frames)
        self.bGoR=np.array([None]*self.frames)
        self.bG=np.array([None]*self.frames)
        self.bR=np.array([None]*self.frames)

        for frame in range(self.frames):
            self.traceG[frame]=np.average(self.dataG[frame][:,self.m1:self.m2],axis=1)
            self.traceR[frame]=np.average(self.dataR[frame][:,self.m1:self.m2],axis=1)
            self.traceGoR[frame]=np.average(self.dataGoR[frame][:,self.m1:self.m2],axis=1)
            self.bGoR[frame]=np.average(self.traceGoR[frame][self.baselineIs[0]:self.baselineIs[1]])
            self.bG[frame]=np.average(self.traceG[frame][self.baselineIs[0]:self.baselineIs[1]])
            self.bR[frame]=np.average(self.traceR[frame][self.baselineIs[0]:self.baselineIs[1]])
            self.dGoR[frame]=self.traceGoR[frame]-self.bGoR[frame]

        self.AVGdGoR=np.average(self.dGoR,axis=0)

    ### FILE STUFF

    def clean(self):
        """delete everything in the analysis folder."""
        for fname in glob.glob(self.folderOut+"/*.*"):
            print("deleting",os.path.basename(fname),'...')
            os.remove(fname)

    def saveData(self,offset=2.46872):
        """generate CSV files of all data and save them in the analysis folder."""
        datadGoR=np.flipud(np.rot90(np.vstack((self.Xs+offset,np.array(self.dGoR.tolist())))))
        dataR=np.flipud(np.rot90(np.vstack((self.Xs+offset,np.array(self.traceR.tolist())))))
        dataG=np.flipud(np.rot90(np.vstack((self.Xs+offset,np.array(self.traceG.tolist())))))
        dataGoR=np.flipud(np.rot90(np.vstack((self.Xs+offset,np.array(self.traceGoR.tolist())))))
        np.savetxt(self.folderOut+"/data_dGoR.csv",datadGoR,delimiter=',',fmt='%.05f')
        np.savetxt(self.folderOut+"/data_dataR.csv",dataR,delimiter=',',fmt='%.05f')
        np.savetxt(self.folderOut+"/data_dataG.csv",dataG,delimiter=',',fmt='%.05f')
        np.savetxt(self.folderOut+"/data_GoR.csv",dataGoR,delimiter=',',fmt='%.05f')
        print("saved multiple raw data CSV files")

    ### PLOTTING ACTIONS
    def shadeBaseline(self):
        plt.axvspan(self.baselineSec[0],self.baselineSec[1],alpha=.1,color='k')

    def markBounds(self,color='y'):
        for xpos in [self.m1,self.m2]:
            plt.axhline(xpos,color=color,ls='--',lw=2)
        for i in self.baselineIs:
            plt.axvline(self.Xs[i],color=color,ls='--',lw=2)

    def saveFig(self,saveAs=None):
        """call this to save a figure. Make saveAs None to display figure. Make it a filename to save it."""
        if saveAs:
            saveAs=os.path.abspath(os.path.join(self.folderOut,saveAs))
            plt.savefig(saveAs,dpi=self.dpi)
            print("saved figure",os.path.basename(saveAs))
        else:
            plt.show()
        plt.close()


    ### FIGURES ####################

    def refFig(self):
        """convert a TIF reference figure showing the linescan path to a PNG in the analysis folder."""
        fname=sorted(glob.glob(self.folder+"/References/*Window2*.tif"))[0]
        fname=os.path.abspath(fname)
        saveAs=os.path.abspath(self.folder+"/analysis/fig_00_ref.png")
        print("converting",fname,'...')
        im = Image.open(fname)
        #print("enhancing contrast...")
        #contrast = ImageEnhance.Contrast(im)
        #im=contrast.enhance(5)
        im.save(saveAs)
        print('saved',saveAs)

    def figureDriftDGOR(self,saveAs=False):
        """create a figure to assess drift of dGoR over time."""
        plt.figure(figsize=(6,6))
        plt.grid(alpha=.5)
        plt.axhline(0,color='k',ls='--')
        plt.title(DELTA+"[G/R] traces by frame")
        for frame in range(self.frames):
            plt.plot(self.Xs,self.dGoR[frame]*100,alpha=.5,label=frame+1,
                     color=plt.cm.get_cmap('jet')(frame/self.frames))
        self.shadeBaseline()
        plt.legend(fontsize=6,loc=1)
        plt.ylabel(DELTA+" [G/R] (%)")
        plt.xlabel("linescan duration (seconds)")
        plt.margins(0,.1)
        plt.tight_layout()
        self.saveFig(saveAs)

    def figureDriftGOR(self,saveAs=False):
        """create a figure to assess drift of dGoR over time."""
        plt.figure(figsize=(6,6))
        plt.grid(alpha=.5)
        plt.title("raw [G/R] traces by frame")
        for frame in range(self.frames):
            plt.plot(self.Xs,self.traceGoR[frame]*100,alpha=.5,label=frame+1,
                     color=plt.cm.get_cmap('jet')(frame/self.frames))
        plt.legend(fontsize=6,loc=1)
        plt.ylabel("raw G/R (%)")
        plt.xlabel("linescan duration (seconds)")
        plt.margins(0,.1)
        plt.tight_layout()
        self.saveFig(saveAs)

    def figureDriftGOR2(self,saveAs=False):
        """create a figure to assess drift of dGoR over time."""
        plt.figure(figsize=(6,6))
        plt.grid(alpha=.5)
        plt.title("raw [G/R] traces by frame")
        for frame in range(self.frames):
            offset=self.Xs[-1]*frame
            plt.plot(self.Xs+offset,self.traceGoR[frame]*100,alpha=.5,label=frame+1,
                     color=plt.cm.get_cmap('jet')(frame/self.frames))
        plt.legend(fontsize=6,loc=1)
        plt.ylabel("raw G/R (%)")
        plt.xlabel("linescan data only (seconds)")
        plt.margins(0,.1)
        plt.tight_layout()
        self.saveFig(saveAs)

    def figureDriftRAW(self,saveAs=False):
        """create a figure to assess drift of R and G over time."""
        plt.figure(figsize=(6,6))

        plt.subplot(211)
        plt.title("average baseline R and G by frame")
        plt.grid(alpha=.5)
        plt.plot(self.bG,'.-',color='g',ms=20)
        plt.plot(self.bR,'.-',color='r',ms=20)
        plt.axis([None,None,0,None])
        plt.ylabel("pixel intensity (AFU)")

        plt.subplot(212)
        plt.title("average baseline G/R ratio by frame")
        plt.grid(alpha=.5)
        plt.plot(self.bGoR,'.-',color='b',ms=20)
        plt.ylabel("raw [G/R]")
        plt.xlabel("frame number")

        plt.tight_layout()
        self.saveFig(saveAs)

    def figureAvg(self,saveAs=False):
        """create a figure showing raw pixel values and dGoR as an average"""
        plt.figure(figsize=(6,6))

        ax1=plt.subplot(211)
        ax2=plt.subplot(212,sharex=ax1)

        plt.subplot(211)
        plt.title(self.name)
        plt.ylabel("raw pixel intensity (AFU)")
        plt.grid(alpha=.5)
        self.shadeBaseline()
        for frame in range(self.frames):
            plt.subplot(211)
            plt.plot(self.Xs,self.traceG[frame],'-',color='G',alpha=.5)
            plt.plot(self.Xs,self.traceR[frame],'-',color='R',alpha=.5)
            plt.subplot(212)
            plt.plot(self.Xs,self.dGoR[frame]*100.0,'-',color='b',alpha=.2)
        plt.subplot(211)
        plt.setp(plt.gca().get_xticklabels(), visible=False)

        plt.subplot(212)
        title=DELTA+" [G/R] (%)"
        if self.frames>1:
            title+=" (avg n=%d)"%self.frames
        plt.ylabel(title)
        plt.grid(alpha=.5)
        self.shadeBaseline()
        plt.axhline(0,color='k',ls='--')
        plt.plot(self.Xs,self.AVGdGoR*100,'-',color='b',alpha=.5)
        plt.margins(0,.1)
        plt.xlabel("linescan duration (seconds)")

        plt.tight_layout()

        self.saveFig(saveAs)

    def figureImg(self,saveAs=False):
        """create a figure showing the actual linescan image with outlined ROI"""
        plt.figure(figsize=(6,6))

        plt.subplot(311)
        plt.title("Line Scan Structure Auto-Detection (avg n=%d)"%self.frames)
        plt.axis([0,self.Xs[-1],0,np.shape(self.dataG)[2]])
        plt.imshow(np.rot90(np.average(self.dataG,axis=0)),cmap='gray',aspect='auto',extent=plt.axis())
        self.markBounds()
        plt.setp(plt.gca().get_yticklabels(), visible=False)
        plt.setp(plt.gca().get_xticklabels(), visible=False)
        plt.ylabel("green channel")
        plt.colorbar()

        plt.subplot(312)
        plt.axis([0,self.Xs[-1],0,np.shape(self.dataR)[2]])
        plt.imshow(np.rot90(np.average(self.dataR,axis=0)),cmap='gray',aspect='auto',extent=plt.axis())
        self.markBounds()
        plt.setp(plt.gca().get_yticklabels(), visible=False)
        plt.setp(plt.gca().get_xticklabels(), visible=False)
        plt.ylabel("red channel")
        plt.colorbar()

        plt.subplot(313)
        plt.axis([0,self.Xs[-1],0,np.shape(self.dataR)[2]])
        data=np.rot90(np.average(self.dataG,axis=0))/np.rot90(np.average(self.dataR,axis=0))*100
        data=data-np.average(data[self.baselineIs[0]:self.baselineIs[1],:])
        plt.imshow(data,cmap='jet',aspect='auto',extent=plt.axis())
        self.markBounds('k')
        plt.setp(plt.gca().get_yticklabels(), visible=False)
        plt.ylabel(DELTA+" [G/R] (%)")
        plt.colorbar()

        plt.xlabel("linescan duration (seconds)")
        plt.tight_layout()

        self.saveFig(saveAs)


    def figure_dGoR_peak(self,saveAs=False,freq=True):
        """create a scatter plot showing the peak dGoR vs frame number."""
        freqs = [1,5,10,15,20,25]
        if freq==True and self.frames==len(freqs):
            Xs=freqs
            xlabel="AP Frequency (Hz)"
        else:
            Xs=np.arange(self.frames)+1
            xlabel="line scan frame number"
        plt.figure(figsize=(6,6))
        plt.grid(alpha=.5)
        Ys=np.ones(self.frames)*np.nan
        plt.title("Calcium Response Curve (peak)")
        for frame in range(self.frames):
            Ys[frame]=np.max(self.dGoR[frame])*100
        print("creating  data_dGoR_byframe_peak ...")
        np.savetxt(self.folderOut+"/data_dGoR_byframe_peak.csv",Ys,delimiter=',',fmt='%.05f')
        plt.ylabel("peak d[G/R] (%)")
        plt.xlabel(xlabel)
        plt.plot(Xs,Ys,'.-',ms=20)
        plt.margins(.1,.1)
        plt.tight_layout()
        self.saveFig(saveAs)

    def figure_dGoR_area(self,saveAs=False,freq=True):
        """create a scatter plot showing the dGoR area vs frame number."""
        freqs = [1,5,10,15,20,25]
        if freq==True and self.frames==len(freqs):
            Xs=freqs
            xlabel="AP Frequency (Hz)"
        else:
            Xs=np.arange(self.frames)+1
            xlabel="line scan frame number"
        plt.figure(figsize=(6,6))
        plt.grid(alpha=.5)
        Ys=np.ones(self.frames)*np.nan
        plt.title("Calcium Response Curve (area)")
        for frame in range(self.frames):
            Ys[frame]=np.sum(self.dGoR[frame])*100/self.Xs[-1]/1000
        print("creating  data_dGoR_byframe_area ...")
        np.savetxt(self.folderOut+"/data_dGoR_byframe_area.csv",Ys,delimiter=',',fmt='%.05f')
        plt.ylabel("d[G/R] area (% * ms)")
        plt.xlabel(xlabel)
        plt.plot(Xs,Ys,'.-',ms=20,color='r')
        plt.margins(.1,.1)
        plt.tight_layout()
        self.saveFig(saveAs)

    ### END OF INDIVIDUAL FIGURES ####################

    def allFigures(self):
        """automatically generate every figure for a given linescan."""
        self.clean()
        self.refFig()
        self.saveData()
        self.figureImg("fig_01_img.png")
        self.figureAvg("fig_02_avg.png")
        if self.frames<3: return
        self.figureDriftRAW("fig_03_drift1.png")
        self.figureDriftDGOR("fig_04_drift2.png")
        self.figureDriftGOR("fig_05_drift3.png")
        self.figureDriftGOR2("fig_05_drift32.png")
        self.figure_dGoR_peak("fig_06_peak.png")
        self.figure_dGoR_area("fig_07_area.png")

    ### END OF FIGURES ####################


def index(folderParent):
    """make index.html and stick it in the parent directory."""
    timestamp=datetime.datetime.now().strftime("%I:%M %p on %B %d, %Y")
    folders=os.listdir(folderParent)
    out="<html><style>"
    out+="""
    img{
        margin: 10px;
        border: 1px solid black;
        box-shadow: 5px 5px 10px rgba(0, 0, 0, .2);
        }
    """
    out+="</style><body>"
    out+="<b style='font-size: 300%%'>pyLineScan</b><br><i>automatic linescan index generated at %s</i><hr><br>"%timestamp
    for folder in sorted(folders):
        if not folder.startswith("LineScan-"):
            continue
        path=os.path.abspath(folderParent+"/"+folder)
        rel=folderParent+"/"+folder
        out+="<div style='background-color: #336699; color: white; padding: 10px; page-break-before: always;'>"
        out+="<span style='font-size: 200%%; font-weight: bold;'>%s</span><br>"%folder
        out+="<code>%s</code></div>"%path
        for fname in sorted(glob.glob(folderParent+"/"+folder+"/analysis/*.png")):
            fname=os.path.basename(fname)
            out+='<a href="%s/analysis/%s"><img src="%s/analysis/%s" height=300></a>'%(rel,fname,rel,fname)
        out+="<br><br><code><b>These data are stored in the following CSV files:</b></code><br>"
        for fname in sorted(glob.glob(folderParent+"/"+folder+"/analysis/*.csv")):
            out+='<code>%s</code><br>'%os.path.abspath(fname)
        out+="<br>"*6
    out+="</code></body></html>"
    fileOut=os.path.abspath(folderParent+"/index.html")
    with open(fileOut,'w') as f:
        f.write(out)
    print("\nSAVED HTML REPORT:\n"+fileOut+'\n')
    webbrowser.open(fileOut)

def analyzeFolderOfLinescans(folderParent,reanalyze=False,matching=False):
    """analyze every linescan folder in a parent directory and generate a report."""
    print("Analyzing folder of linescans:",folderParent)
    print(" reanalyze =",reanalyze)
    folders=sorted(glob.glob(folderParent+'/LineScan-*'))
    for folder in folders:
        if os.path.exists(folder+"/analysis/data_GoR.csv") and not reanalyze:
            print("not re-analyzing",folder)
            continue
        if matching and not matching in os.path.basename(folder):
            continue
        LS=LineScan(folder)
        LS.allFigures()
    #index(folderParent)
    return

if __name__=="__main__":
    if len(sys.argv)==1:
        print("### RUNNING WITHOUT ARGUMENTS - ASSUMING YOU ARE A DEVELOPER ###\n"*20)
        folder=r'X:\Data\SCOTT\2017-06-16 OXT-Tom\2p'
        analyzeFolderOfLinescans(folder,reanalyze=True,matching="-661")
    else:
        reanalyze=False
        if "reanalyze" in sys.argv:
            print("FORCING RE-ANALYSIS OF ALL FILES.")
            reanalyze=True
        folder=os.path.abspath(sys.argv[1])
        print("FOLDER TO ANALYZE:\n%s"%folder)
        assert os.path.exists(folder)
        analyzeFolderOfLinescans(folder,reanalyze=reanalyze)
    print("FINISHED ANALYSIS SUCCESSFULLY")