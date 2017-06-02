import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
np.set_printoptions(suppress=True) # don't show exponential notation
import os
import subprocess
import sys
import glob
import shutil

class TiffVid:
    def __init__(self,folder,clean=False):
        print("LOADING TIFF VIDEO",folder)
        self.folder=folder
        if clean:
            self.clean()
        self.loadTXT(os.path.join(folder,"experiment.txt"))
        self.loadTSV(os.path.join(folder,"results.xls"))
        self.calcdFF()

    def clean(self):
        """delete all files in this folder except for the experiment files."""
        print("cleaning out old data...")
        for fname in os.listdir(self.folder):
            if fname.startswith("results_") or \
               fname.startswith("fig_"):
               print(" DELETING",fname)
               os.remove(self.folder+"/"+fname)

    def loadTXT(self, fname):
        """load a text file and return its content as a dictionary"""
        fname=fname[:-4]+".txt"
        if not os.path.exists(fname):
            print("WARNING: experiment file does not exist, so I'll make one.")
            with open(fname,'w') as f:
                f.write("")
        with open(fname) as f:
            raw=f.readlines()
        conf={"baseline":[0,1],"period":10}
        for line in raw:
            line=line.strip()
            if line.startswith("#"): continue
            if line.count("=")==1:
                var,val=line.split("=")
                vals=val.split("-")
                for i in range(len(vals)):
                    vals[i]=float(vals[i])
                if len(vals)==1:
                    vals=vals[0]
                conf[var]=vals
                print("",var,"=",vals)
        self.conf=conf

    def loadTSV(self, fname):
        """
        load a CSV generated by ImageJ and return it as a numpy array.
        Returns data in the same shape as it exists in the CSV.
        """
        print("loading data from:",fname)
        with open(fname) as f:
            raw=f.read()
        raw=raw.replace("\t",",")
        raw=raw.split("\n")
        labels=raw[0].strip().split(",")
        labels[0]="frame"
        raw=raw[1:]
        nRows=len(raw)
        nCols=len(labels)
        data=np.empty((nRows,nCols))
        data[:]=np.nan
        for row in range(nRows):
            if raw[row].count(","):
                data[row]=raw[row].split(",")
        if np.all(np.isnan(data[-1])):
            data=data[:-1]
        print("loaded %d lines of data from %d ROIs"%(nRows,nCols-1))
        self.data=np.transpose(data)
        self.dataYlabel="raw pixel value"
        self.dataX=np.arange(len(data))*self.conf['period']/60
        self.dataXlabel="experiment duration (minutes)"

    def calcdFF(self,subtractOutFirstROI=True):
        """
        once raw pixel values are in self.data, run this to convert to dF/F.
        I'm using the variable names shown on the GitHub:
        github.com/swharden/ROI-Analysis-Pipeline/blob/master/doc/theory.jpg
        """
        b1=int(self.conf['baseline'][0])
        b2=int(self.conf['baseline'][1])
        for i,f in enumerate(self.data[1:]):
            b=np.average(f[b1:b2])
            r=f/b # baseline-adjusted raw fluorescence intensity
            d=(r-1)*100 # delta F / F in percent (%)
            self.data[i+1]=d # push this ROI dF/F (d) back into the data.
        self.dataYlabel=r'$\Delta$'+"F/F (%)"
        if subtractOutFirstROI:
            self.data[1:]=self.data[1:]-self.data[1]

    def renderVideo(self,overwrite=False):
        if overwrite is False and os.path.exists(self.folder+"/render.mp4"):
            print("VIDEO ALREADY EXISTS")
            return
        fnames=sorted(glob.glob(self.folder+"/*.tif"))
        self.maxIntensity=False # optionally define this here
        for frame in range(len(self.dataX)):
            print("Processing frame %d of %d (%.02f%%)"%(frame,len(self.dataX),100*frame/len(self.dataX)))
            fname=fnames[frame]
            fname=os.path.join(self.folder,fname)
            self.figure_tiff_and_graph(fnamePic=fname,frame=frame)
        cmd=r'C:\Users\swharden\Documents\important\ffmpeg\bin\ffmpeg.exe'
        cmd+=r' -y -i "%s\video\frame_%%07d.png"'%self.folder
        cmd+=r' -c:v libx264 -pix_fmt yuv420p "%s"'%os.path.join(self.folder,"render.mp4")
        print(cmd)
        os.system(cmd)
        #shutil.rmtree(os.path.join(self.folder,"video"))
        print("CREATED VIDEO:\n",os.path.join(self.folder,"render.mp4"))


    ###########################################################################
    ### FIGURES ###############################################################
    ###########################################################################

    def figure_shade(self):
        """read the conf and shade the regions it contains."""
        colors=['r','g','b','o','m','k','y']
        for i,key in enumerate(self.conf):
            if type(self.conf[key]) is list and len(self.conf[key])==2:
                plt.axvspan(self.conf[key][0]*self.conf['period']/60,
                            self.conf[key][1]*self.conf['period']/60,
                                alpha=.1,lw=0,label=key,
                                color=colors[i])

    def fig_traces(self):
        plt.figure(figsize=(8,6))
        plt.axhline(0,lw=1,color='k',ls='--')
        for i in range(2,len(self.data)):
            plt.plot(self.dataX,self.data[i],color='k',lw=2,alpha=.2)
        plt.plot(self.dataX,np.average(self.data[2:],axis=0),color='k',lw=2,alpha=1,ls='-',label="average")
        plt.grid(alpha=.5)
        self.figure_shade()
        plt.margins(0,.1)
        plt.legend(fontsize=11)
        plt.ylabel(self.dataYlabel,fontsize=16)
        plt.xlabel(self.dataXlabel,fontsize=16)
        plt.title("ROI Traces [%s]"%os.path.basename(self.folder),fontsize=20)
        plt.savefig(self.folder+"/fig_traces.png",dpi=100)
        plt.tight_layout()
        plt.show()
        plt.close()

    def fig_av(self,stdErr=False):
        plt.figure(figsize=(8,6))
        XS=self.data[0]*self.conf['period']/60
        AV=np.average(self.data[2:],axis=0)
        ERR=np.std(self.data[2:],axis=0)
        errorType="stDev"
        if stdErr:
            ERR=ERR/np.sqrt(len(self.data[2:]))
            errorType="stdErr"
        plt.axhline(0,lw=1,color='k',ls='--')
        plt.fill_between(XS,AV-ERR,AV+ERR,
                         alpha=.1,label=errorType,lw=0,color='k')
        plt.plot(XS,AV,color='k',label="average",lw=2)
        plt.grid(alpha=.5)
        self.figure_shade()
        plt.margins(0,.1)
        plt.legend(fontsize=11)
        plt.ylabel(r'$\Delta$'+"F/F (%)",fontsize=16)
        plt.xlabel("experiment duration (minutes)",fontsize=16)
        plt.title("ROI Traces [%s]"%os.path.basename(self.folder),fontsize=20)
        plt.savefig(self.folder+"/fig_av.png",dpi=100)
        plt.tight_layout()
        plt.show()
        plt.close()

    ###########################################################################




    def figure_raw_all_highlight(self,upToFrame=-1):
        """
        render an image ready for video overlay showing all ROI traces
        and highlighting up to a certain frame.
        """
        plt.figure(figsize=(8,6))
        if upToFrame<0:
            upToFrame=len(self.data[0])
        for i in range(1,len(self.data)):
            offsetX=i*1
            offsetY=i*2
            plt.plot(offsetX+self.dataBL[0]*self.conf['period']/60,
                     offsetY+self.dataBL[i],
                     color='k',alpha=.2,lw=1)

            plt.plot(offsetX+self.dataBL[0][:upToFrame]*self.conf['period']/60,
                     offsetY+self.dataBL[i][:upToFrame],
                     color='y',alpha=.5,lw=3)

        plt.axis('off')
        plt.margins(0,.1)
        plt.tight_layout()
        #plt.savefig("01-raw.png",dpi=100)
        plt.show()
        plt.close()

    def figure_tiff_and_graph(self,fnamePic='../data/sample.jpg',frame=-1):
        # create the individual PNG files to be used for video creation
        from read_roi import read_roi_zip

        # PREPARE THE FIGURE
        mult=1
        plt.figure(figsize=(16*mult,9*mult))
        gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])

        # LEFT AXES - FIGURE
        ax0 = plt.subplot(gs[0])
        img=plt.imread(fnamePic)
        if self.maxIntensity is False:
            self.maxIntensity=np.max(img)
            print("SETTING MAX INTENSITY:",self.maxIntensity)
        ax0.imshow(img, zorder=0, cmap='gray', clim=(0, self.maxIntensity))
        roiFile=self.folder+"/RoiSet.zip"
        if os.path.exists(roiFile):
            rois = read_roi_zip(roiFile)
            for p,roi in enumerate(rois):
                color='y'
                if p==0:
                    color='c'
                X1,Y1=rois[roi]['left'],rois[roi]['top']
                X2,Y2=rois[roi]['width']+X1,rois[roi]['height']+Y1
                ax0.plot([X1,X2,X2,X1,X1],[Y1,Y1,Y2,Y2,Y1],
                         color=color,alpha=.5,lw=2)
                ax0.text(X1+1,Y1+5,str(p+1),va='top',color=color,
                         fontsize='small',fontweight='bold')

        miscmsg="GABA Cre / GCaMP6f [PFC]\n"
        msg="%s\n%sframe:%d\nminutes: %.02f"%(self.folder,miscmsg,frame,self.dataX[frame])
        ax0.text(2,2,msg,va='top',color='k',fontsize='small',fontweight='bold')
        ax0.text(0,0,msg,va='top',color='w',fontsize='small',fontweight='bold')

        plt.margins(0,0)
        plt.axis('off')

        # RIGHT AXES - GRAPHS
        ax1 = plt.subplot(gs[1])
        if frame<0:
            frame=len(self.data[0])

        offsetX=0
        offsetY=-10
        for i in range(1,len(self.data)):
            if i==1:
                msg="baseline"
            else:
                msg=str(i)

            ax1.text(0,offsetY*i-offsetY*.2,msg)
            ax1.plot(offsetX*i+self.dataX,
                     offsetY*i+self.data[i],
                     color='k',alpha=.2,lw=1)
            ax1.plot(offsetX*i+self.dataX[:frame],
                     offsetY*i+self.data[i][:frame],
                     color='b',alpha=.5,lw=1)
        self.figure_shade()
        plt.axis('off')
        plt.margins(0,.05)

        # FIX UP THE FIGURE, SAVE, AND SHOW
        plt.tight_layout()
        bn=os.path.dirname(os.path.abspath(fnamePic))
        if not os.path.exists(bn+"/video/"):
            os.mkdir(bn+"/video/")
        plt.savefig(bn+"/video/frame_%07d.png"%frame)
#        plt.show()
        plt.close('all')

if __name__=="__main__":
    #path=r"X:\Data\SCOTT\2017-05-10 GCaMP6f\2017-05-10 GCaMP6f PFC OXTR cre\2017-05-31 cell1"
    #path=r"C:\Users\swharden\Documents\temp\seq"

    for folder in sorted(glob.glob(r"X:\Data\SCOTT\2017-05-10 GCaMP6f\2017-05-10 GCaMP6f PFC OXTR cre\*")):
        if not os.path.isdir(folder):
            continue
        print("\n\n\n","#"*100,"\n"," ANALYZING",folder,"\n","#"*100)
#        try:
        TV=TiffVid(folder)
        TV.renderVideo(overwrite=True)
#        except:
#            print("EXCEPTION")

#    TV.fig_traces()
#    TV.fig_av()
    #TV.figure_BL_avg()
    #TV.figure_raw_all_highlight()

    print("DONE")