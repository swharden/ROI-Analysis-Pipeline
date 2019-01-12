"""
core class to analze Time Series data from the two-photon microscope
"""

import os
import numpy as np
import matplotlib.image as mpimg
import time
from read_roi import read_roi_zip
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import glob
import webbrowser
import winsound

COLORMAPS = sorted([m for m in cm.cmap_d if not m.endswith("_r")])
DELTA=R"$\Delta$"

HTML_TEMPLATE="""<html><head><style>
body {font-family: sans;}
</style></head><body>BODY</body></html>"""

### ROI OPERATIONS

def roi_areas(roiFile):
    """
    Given an ROI zip (created with ImageJ's ROI Manager), analyze each
    ROI and return a dictionary with its keys including 'area' which is
    a list of X/Y pixel pairs encircled by the ROI.

    Also adds a 'bounds' key [X1,X2,Y1,Y2] of the bounds of the ROI
    based on its area.

    Unsupported shapes will have their bounds detected automatically and
    convereted into rectangles.
    """

    assert os.path.exists(roiFile)
    rois = read_roi_zip(roiFile)
    print("Found %d ROIs in %s"%(len(rois),os.path.basename(roiFile)))

    # this is a hack to turn unsupported shapes into rectangles
    # just set its top,left,width, and height and change type to rectangle
    for i,roi in rois.items():
        if roi['type'] in ['freehand','polygon']:
            print("  ROI %d '%s' %s->rectangle"%(i+1,roi['name'],roi['type']))
            Xs,Ys=roi['x'],roi['y']
            X1,X2,Y1,Y2=np.min(Xs),np.max(Xs),np.min(Ys),np.max(Ys)
            rois[i]['left'],rois[i]['top']=X1,Y1
            rois[i]['width'],rois[i]['height']=X2-X1,Y2-Y1
            rois[i]['type']='rectangle'
        if roi['type'] in ['oval']:
            rois[i]['type']='rectangle'

    # set the 'area' and 'bounds' of each ROI
    print("ROIs which will be used:")
    #for i,roi in rois.items():
    for n,i in enumerate(rois):
        roi=rois[i]

        # populate keys for rectangles
        if roi['type'] is 'rectangle':
            X1,Y1=roi['left'],roi['top']
            X2,Y2=roi['width']+X1,roi['height']+Y1
            area=[]
            for x in range(X1,X2):
                for y in range(Y1,Y2):
                    area.append((x,y))
            rois[i]['area']=area

        else: #TODO: add eclipse and polygon support
            print("WARNING: unsupported ROI type:",roi['type'])

        # calculate bounds of a shape based on its area
        if 'area' in rois[i].keys():
            Xs,Ys=[],[]
            for X,Y in rois[i]['area']:
                Xs.append(X)
                Ys.append(Y)
            rois[i]['bounds']=np.min(Xs),np.max(Xs),np.min(Ys),np.max(Ys)

        print("  ROI '%s' covers %d pixels"%(roi['name'],
                                                len(roi['area'])))

    return rois

### IMAGE ANALYSIS
def image_roi_average(img3d,roi):
    """given a SINGLE roi, return the average of its area by frame."""
    AVGs=np.empty(len(img3d))
    for frame in range(len(img3d)):
        values=np.empty(len(roi['area']))
        for i,pair in enumerate(roi['area']):
            values[i]=img3d[frame,pair[1],pair[0]]
        AVGs[frame]=np.average(values)
    #print("WARNING: LOWPASSING")
    #AVGs=lowpass(AVGs,10)
    return AVGs

def blur2D(image2D,sigmaFrac=10):
    """given an image, blur it by sigma, and return it."""
    #NOTE: sigma may not be number of pixels
    ftimage = np.fft.fftshift(np.fft.fft2(image2D))
    ncols, nrows = image2D.shape
    cy, cx = nrows/2, ncols/2
    sigmax,sigmay=ncols/sigmaFrac,nrows/sigmaFrac
    x = np.linspace(0, nrows, nrows)
    y = np.linspace(0, ncols, ncols)
    X, Y = np.meshgrid(x, y)
    gmask = np.exp(-(((X-cx)/sigmax)**2 + ((Y-cy)/sigmay)**2))
    return np.abs(np.fft.ifft2(ftimage * gmask))

### FOLDER AND DATA ANALYSIS

def xml_parse_prairie(xmlFileName,verbose=True):
    """
    given the path any prairie XML file, parse it and return a dictionary with
    the useful info. Useful info involves fields defined in the 'key' list
    below. Keys which aren't found in the XML will just be ignored.

    This function should work for TSeries, ZSeries, SingleImage, etc. and is
    coded in such a way that it should survive even as prairie updates their
    XML format.
    """
    if verbose:
        print("parsing",os.path.basename(xmlFileName))
    assert os.path.exists(xmlFileName), "can't find "+xmlFileName
    with open(xmlFileName) as f:
        xml=f.read()
        xml=xml.split(">")
        for i,line in enumerate(xml):
            xml[i]=line.strip()
        xml="".join(xml)
    conf={}
    for key in ['opticalZoom','objectiveLens', # physical lens
                'pixelsPerLine','linesPerFrame', # dimensions
                'dwellTime','framePeriod','scanLinePeriod' # pixel timing
                'laserPower', # laser settings
                'pmtGain~1~','pmtGain~2~', # PMT settings
                'INTENTIONAL_FAILURE', # just testing
                ]:
        val=xml_value_from_key(xml,key)
        if val is not None:
            conf[key.replace("~",'')]=val
    times=[float(x.split('"')[1]) for x in xml.split("absoluteTime=")[1:]]
    conf["times"]=np.array(times)
    if verbose and len(conf.keys()):
        print("XML parsing produced:")
        for key in sorted(conf.keys()):
            if key is 'times':
                print("  times=[%d points]"%len(times))
            else:
                print("  %s=%s"%(key,conf[key]))
    return conf

def xml_value_from_key(xml,match,matchNumber=1):
    """
    Given a huge string of XML, find the first match
    of a given a string, then go to the next value="THIS"
    and return the THIS as a string.

    if the match ends in ~2~, return the second value.
    """
    for i in range(1,10):
        if match.endswith("~%d~"%i):
            match=match.replace("~%d~"%i,'')
            matchNumber=i
    if not match in xml:
        return None
    else:
        val=xml.split(match)[1].split("value=",3)[matchNumber]
        val=val.split('"')[1]
    try:
        val=float(val)
    except:
        val=str(val)
    return val

def images_to_numpy(imageList,saveAs):
    """
    Given a list of images, create a 3D numpy array to represent them and
    save it as a given filename (ending in .npy). All images must be
    identical dimensions. Saves the data, and also returns it.

    Alternatively, if the save path already exists, just load and return it.
    """
    saveAs=os.path.abspath(saveAs)
    if os.path.exists(saveAs):
        print("loading data from %s ..."%(os.path.basename(saveAs)))
        data=np.load(saveAs)
        if len(data)==len(imageList):
            print("  loaded %.02f MB array"%(data.nbytes/2**20),data.shape)
            return data
        else:
            print("... but I see %d images! Starting over."%(len(imageList)))
    # we have to create the data file
    for n,fname in enumerate(imageList):
        imageData=mpimg.imread(fname)
        if n==0:
            sizeY,sizeX=imageData.shape
            data=np.empty((len(imageList),sizeY,sizeX))
            print("creating data for %s ..."%(os.path.basename(saveAs)))
        elif n%20==0:
            print("  %.02f%% ..."%(100*n/len(imageList)))
        data[n]=imageData
    print("saving %.02f MB array to disk ..."%(data.nbytes/1024/1024))
    np.save(saveAs,data)
    print("created:",saveAs)
    return data

def clock_to_float(s):
    """given '7:30' return 7.5"""
    if ":" in s:
        M,S=[int(x) for x in s.split(":")]
        return round(float(M+S/60.0),2)
    else:
        return float(s)

def tags_load(folder):
    """
    Look for folder/experiment.txt and load its contents. If it doesn't
    exist, create it as a blank text file.
    It should be formatted like:
        baseline=3:00-7:00 # important!
        GABA=7:30-9:30
        TGOT=12:22-15:45
        demo=17-30 # also works
        name with spaces=12-53 # fine too
        bubble=12:34 # single line okay
    """
    tags=[]
    fname=os.path.join(folder,"experiment.txt")
    if not os.path.exists(fname):
        print("creating empty",os.path.basename(fname))
        with open(fname,'w') as f:
            f.write('')
    with open(fname) as f:
        raw=f.read().split("\n")
    for line in raw:
        line=line.strip().split("#")[0]
        if not "=" in line:
            continue
        tag,vals=[x.strip() for x in line.split('=')]
        vals=[clock_to_float(x) for x in vals.split('-')]
        tags.append([tag]+vals)
    tags.sort(key=lambda x: x[1])
    if len(tags) and not 'baseline' in [x[0] for x in tags]:
        print("  Tags found but no baseline found! Inventing one.")
        BL1=1
        BL2=tags[0][1]-1
        if BL2<BL1:
            BL2=BL1+1
        tags.insert(0,['baseline',BL1,BL2])
    if len(tags):
        print("Tags found in %s:"%os.path.basename(fname))
        for tag in tags:
            print("  %s = %s"%(tag[0],str(tag[1:])))
    return tags

### PLOTTING

def plot_saveOrShow(saveAs,show):
    # if a filename is given, save it. Otherwise show it.
    if saveAs:
        saveAs=os.path.abspath(saveAs)
        print("  saving",saveAs)
        plt.savefig(saveAs)
    if show is False:
        return # don't show no matter what
    if show is True:
        plt.show()
        return # show because we told it to
    if show is None and saveAs is False:
        plt.show() # show becase we didn't save
    plt.close('all')

def plot_image(image2d,colorbar=True,cm=None,percentile=(None,None)):
    """
    given a 2D array, plot it with a colormap scale bar.
    """
    from matplotlib.colors import LinearSegmentedColormap
    cmDefault='gray'
    if type(cm) is str:
        if cm.lower() in 'red green blue magenta':
            cm = LinearSegmentedColormap.from_list(cm,['black', cm])
        elif not cm in COLORMAPS:
            print("WARNING: colormap '%s' is invalid. Consider:"%cm)
            [print("  "+x) for x in COLORMAPS]
            cm=None
    if not cm:
        cm=cmDefault
    if percentile[0] is None:low=np.min(image2d)
    else:low=np.percentile(image2d,percentile[0])
    if percentile[1] is None:high=np.max(image2d)
    else:high=np.percentile(image2d,percentile[1])
    plt.imshow(image2d,cmap=cm,clim=(low,high))
    if colorbar:
        plt.colorbar()

def plot_add_tags(tags,seconds=False):
    """
    given a specially formatted tags list (see that function), add
    shading, labels, vertical lines, etc. where appropraite.
    Assume the matplotlib figure is already selected.
    """
    for i,tag in enumerate(tags):
        #color=plt.get_cmap('Dark2')(tag[1]/tags[-1][1])
        color=plt.get_cmap('Dark2')(i/len(tags))
        name,vals=tag[0],tag[1:]
        if seconds:
            vals=[x*60 for x in vals]
        if len(vals)==2:
            plt.axvspan(vals[0],vals[1],color=color,alpha=.2,label=name)
        else:
            for val in vals:
                plt.axvline(val,color='r',alpha=.5,lw=2,ls='--',label=name)
    return

def plot_roi_bounds(bounds,color='w',label=False):
    """
    with an existing 2d image shown, plot its outline.
    bounds=[X1,X2,Y1,Y2]
    """
    X1,X2,Y1,Y2=bounds
    plt.plot([X1,X2,X2,X1,X1],[Y1,Y1,Y2,Y2,Y1],'-',color=color)
    if label:
        plt.text(X1,Y1-3,label,verticalalignment='bottom',color=color,
                 backgroundcolor=(0,0,0,.5))
    plt.margins(0,0)

def nozero(arr):
    """
    given a numpy array, make every 0 value the next closest minimum value
    so it can be divided by without throwing div/0 error.
    """
    vals=sorted(list(set(np.array(arr).flatten())))
    if vals[0]<0:
        print("correcting for div/zero by replacing 0 with",vals[1])
        arr[arr==0]=vals[1]
    return arr

### 2P FOLDER CLASSES


def lowpass(data,filterSize=None):
    """
    minimal complexity low-pass filtering.
    Filter size is how "wide" the filter will be.
    Sigma will be 1/10 of this filter width.
    If filter size isn't given, it will be 1/10 of the data size.
    """

    def convolve(signal,kernel):
        pad=np.ones(len(kernel)/2)
        signal=np.concatenate((pad*signal[0],signal,pad*signal[-1]))
        signal=np.convolve(signal,kernel,mode='same')
        signal=signal[len(pad):-len(pad)]
        return signal

    def kernel_gaussian(size=100, sigma=None, forwardOnly=False):
        if sigma is None:
            sigma=size/10
        size=int(size)
        points=np.exp(-np.power(np.arange(size)-size/2,2)/(2*np.power(sigma,2)))
        if forwardOnly:
            points[:int(len(points)/2)]=0
        return points/sum(points)

    if filterSize is None:
        filterSize=len(data)/10
    kernel=kernel_gaussian(size=filterSize)
    data=convolve(data,kernel) # do the convolution with padded edges
    return data




class TSeries:
    def __init__(self,folder):
        """initialize with a time series folder."""

        # figure our our paths and file names
        t1=time.perf_counter()
        self.folder=os.path.abspath(folder)
        self.ID=os.path.basename(folder)
        print("loading from:",self.folder)
        assert os.path.exists(self.folder), \
            "folder does not exist: "+self.folder
        self.folderSave=os.path.join(self.folder,"SWH2P")
        if not os.path.exists(self.folderSave):
            os.mkdir(self.folderSave)
        self.files=sorted(os.listdir(folder))
        self.files=[os.path.join(self.folder,x) for x in self.files]
        self.filesCH1=[x for x in self.files if '_Ch1_' in x \
                       and os.path.basename(x).endswith(".tif") \
                       and os.path.basename(x).startswith("TSeries")]
        self.filesCH2=[x for x in self.files if '_Ch2_' in x \
                       and os.path.basename(x).endswith(".tif") \
                       and os.path.basename(x).startswith("TSeries")]
        assert len(self.filesCH1)==len(self.filesCH2), \
            "channels have a different number of TIFs!"

        # find and load XML data into self.conf
        xmlFiles=[x for x in self.files if x.endswith('.xml') \
                      and x.replace('.xml','.env') in self.files]
        assert len(xmlFiles) is 1, "cannot find matching .xml and .env file"
        self.conf=xml_parse_prairie(xmlFiles[0])
        self.timeS=self.conf['times']
        self.timeM=self.conf['times']/60
        self.timeH=self.conf['times']/60/60

        # load 3D numpy arrays (creating and saving them if needed)
        self.R=images_to_numpy(self.filesCH1,self.folderSave+"/data_CH1.npy")
        self.G=images_to_numpy(self.filesCH2,self.folderSave+"/data_CH2.npy")

        # our shutter several ms to open and pollutes the first frame.
        print("correcting for shutter glitch.")
        self.G[0]=self.G[1]
        self.R[0]=self.R[1]

        print("preparing averages...")
        self.Ravg=np.average(self.R,axis=0)
        self.Gavg=np.average(self.G,axis=0)

        print("preparing standard deviations...")
        self.Rstd=nozero(np.std(self.R,axis=0))
        self.Gstd=nozero(np.std(self.G,axis=0))

        print("preparing G/R ratios...")
        self.GoR=self.G/nozero(self.R)
        self.GoRavg=np.average(self.GoR,axis=0)

        print("loading experiment tags and ROIs...")
        self.tags=tags_load(self.folder)
        self.roisDict=roi_areas(os.path.join(self.folder,"RoiSet.zip"))
        self.rois=list(self.roisDict.values())

        print("calculating delta G/R...")
        self.deltaGoverRs()
        SVdGoRs=np.rot90(self.dGoRs)
        SVdGoRs=np.insert(SVdGoRs,0,self.timeM,axis=1)
        np.savetxt(self.folderSave+"/dGoRs.csv",SVdGoRs,fmt='%.05f',
                   delimiter=', ',
                   header="time,"+",".join(list(self.roisDict.keys())))
        print("saved",self.folderSave+"/dGoRs.csv")

        # figure out how long it took to load
        print('completed loading data in %.03f sec'%(time.perf_counter()-t1))
        print("-"*60)

    def roi_average(self,image3d,roiNumber):
        """
        given a 3D image, return the frame by frame averge by ROI number.
        """
        assert roiNumber<len(self.rois)
        return image_roi_average(image3d,self.rois[roiNumber])

    def deltaGoverR(self,roiNumber,baselinePercentile=20,method=2):
        """
        Returns the baseline G/R (1d array) of the given ROI).
        Lower percentile is used instead of baseline subtraction.

        Args:
            roiNumber (int): roi number to be analyzed
            baselinePercentile (int,float): lower percentile for baseline
              calcullation. Note that baseline is from baselineFrames()
            method (int): which delta calculation to use:
                if 1: returns (dG)/R
                if 2: returns d(G/R)
        """
        assert roiNumber<len(self.rois)

        if method is 1:
            # returns (dG)/R
            G=self.roi_average(self.G,roiNumber)
            BL=np.percentile(G[self.baselineFrames()],baselinePercentile)
            return 100*(G-BL)/self.roi_average(self.R,roiNumber)

        elif method is 2:
            # returns d(G/R)
            GoR=self.roi_average(self.GoR,roiNumber)
            BL=np.percentile(GoR[self.baselineFrames()],baselinePercentile)
            return 100*(GoR-BL)

    def deltaGoverRs(self,baselinePercentile=20,save=True):
        """
        Creates the dG/R of every ROI (2d array, %dG/R).
        Just calls deltaGoverR() for every ROI.
        """
        self.dGoRs=np.empty((len(self.rois),len(self.timeH)))*np.nan
        for roiNum in range(len(self.rois)):
            try:
                self.dGoRs[roiNum]=self.deltaGoverR(roiNum,baselinePercentile)
            except:
                print("FAILED ON ROI:",roiNum)
                winsound.Beep(440, 1000) # frequency, duration

    def plot_tags(self,seconds=False):
        """
        Decorate the current matplotlib plot with tag markers/shades.
        This assumes your horizontal axis is in minutes. If it's in seconds,
        set secods=True and it will know what to do.
        """
        plot_add_tags(self.tags,seconds)
        return

    def baselineFrames(self):
        """
        Returns a list of frames in the 'baseline' tag.
        If that tag doesn't exist, return only the first frame.
        """
        frames=[]
        for tag,T1,T2 in [x for x in self.tags if x[0]=='baseline']:
            for i,timePoint in enumerate(self.conf['times']):
                if timePoint>=T1*60 and timePoint<=T2*60:
                    frames.append(i)
            return frames
        else:
            return [0]

    ### FIGURES
    def figure_dGoR_roi(self,showEach=True,rois='all',
                        saveAs=False,show=None):
        """
        Show a delta G/R plot like you'd see in a publication.
        You can define rois individually, or plot them all.
        Averages may also be plotted (perhaps with stdev).
        You can save the figure (as PNG) and/or show it.

        Args:
            showEach: whether or not to plot each ROI as a colored trace
            rois: determines what to plot/average
                if str - analyze every ROI
                if int - analyze only that ROI number
                if list - analyze these ROI numbers
            saveAs: if a string is given, save the figure as this filename
        """

        #TODO: average only plotted ROIs.

        # prepare list of ROIs to plot
        if type(rois) is str:
            rois=list(range(len(self.rois)))
        elif type(rois) == int:
            rois=[int(rois)]
        assert type(rois) is list
        for n in rois:
            assert n>=0 and n<len(self.rois)

        # prepare the figure
        plt.figure(figsize=(15,5))
        plt.grid()
        plt.ylabel("%"+DELTA+"G/R",fontsize=20)
        plt.title(self.ID,fontsize=20)
        plt.axhline(0,color='k')
        self.plot_tags()

        if showEach:
            for roi in rois:
                plt.plot(self.timeM,self.dGoRs[roi],alpha=.5,lw=2,
                         label=self.rois[roi]['name'])

        if len(rois)>1:
            # plot the average (and maybe stdev) traces
            avg=np.average(self.dGoRs[rois],axis=0)
            err=np.std(self.dGoRs[rois],axis=0)
            plt.plot(self.timeM,avg,color='k',lw=3,label='average')
            if not showEach:
                plt.fill_between(self.timeM,avg-err,avg+err,lw=0,color='k',
                                 alpha=.2,label='stdev')

        # make a fancy legend outside the plot area
        plt.tight_layout()
        box = plt.gca().get_position()
        plt.gca().set_position([box.x0, box.y0, box.width * 0.8, box.height])
        plt.gca().legend(loc='center left', bbox_to_anchor=(1, .7))
        plt.margins(0,0)

        if saveAs:
            saveAs=os.path.join(self.folderSave,saveAs)
        plot_saveOrShow(saveAs,show)

    def figure_roi_inspect(self,roiNumber,percentile=(1,99),
                           saveAs=False,show=None):
        """
        Given an ROI (number), create a figure to show G, R, G/R, and d(G/R).
        """
        channels=[[231,"CH1 (red) average",self.Ravg,'magenta'],
                  [232,"CH2 (green) average",self.Gavg,'green'],
                  [234,"G/R average",self.GoRavg,'gray'],
                  [235,"Gstd/Ravg",self.Gstd/self.Ravg,'jet'],
                  ]

        plt.figure(figsize=(16,10))
        for i,channel in enumerate(channels):
            subplot,label,image2d,color=channel
            label+=" [ROI %d]"%(roiNumber)
            plt.subplot(subplot)
            plt.title(label)
            plot_image(image2d,percentile=percentile,cm=color)
            plot_roi_bounds(self.rois[roiNumber]['bounds'])

        plt.subplot(233)
        plt.title("[ROI %d] raw PMT values (12-bit)"%(roiNumber))
        plt.grid()
        plot_add_tags(self.tags)
        plt.plot(self.timeM,self.roi_average(self.G,roiNumber),
                 color='g',alpha=.5,lw=2,label="G")
        plt.plot(self.timeM,self.roi_average(self.R,roiNumber),
                 color='r',alpha=.5,lw=2,label="R")
        plt.margins(0,.1)

        plt.subplot(236)
        plt.title("[ROI %d] G/R (ratio)"%(roiNumber))
        plt.grid()
        plot_add_tags(self.tags)
        plt.plot(self.timeM,self.roi_average(self.GoR,roiNumber),
                 color='b',alpha=.5)
        plt.margins(0,.1)
        plt.tight_layout()

        if saveAs:
            saveAs=os.path.join(self.folderSave,saveAs)
        plot_saveOrShow(saveAs,show)

        # plot just the d[G/R]
        plt.figure(figsize=(20,6))
        plt.title("[ROI %d] G/R (ratio)"%(roiNumber))
        plt.grid()
        plot_add_tags(self.tags)
        plt.plot(self.timeM,self.roi_average(self.GoR,roiNumber),
                 color='b',alpha=.5)
        plt.margins(0,.1)
        plt.tight_layout()
        if saveAs:
            saveAs=saveAs.replace(".png","_dGR.png")
        plot_saveOrShow(saveAs,show)


    def figure_roi_inspect_all(self):
        """creates/saves individual charts for every ROI."""
        for roiNumber in range(len(self.rois)):
            self.figure_roi_inspect(roiNumber,saveAs="roi_%02d.png"%roiNumber)

    def figure_rois(self):
        """draw the original data and label every ROI"""
        channels=[[221,"CH1 (red) average",self.Ravg,'magenta'],
                  [222,"CH2 (green) average",self.Gavg,'green'],
                  [223,"G/R average",self.GoRavg,'gray'],
                  [224,"Gstd/Ravg",self.Gstd/self.Ravg,'jet'],
                  ]

        plt.figure(figsize=(16,12))
        for roiNumber in range(len(self.rois)):
            for i,channel in enumerate(channels):
                subplot,label,image2d,color=channel
                label+=" [ROI %d]"%(roiNumber)
                plt.subplot(subplot)
                plt.title(label)
                plot_image(image2d,cm=color,colorbar=(roiNumber==0),
                           percentile=(1,99))
                plot_roi_bounds(self.rois[roiNumber]['bounds'],
                                label=roiNumber+1)
        plt.tight_layout()
        plot_saveOrShow(self.folderSave+"/roiAll.png",show=False)

    def cleanUp(self):
        """deletes every non-npy file in the save folder."""
        print("  cleaning up",self.folderSave)
        for fname in glob.glob(self.folderSave+"/*.*"):
            if not fname.endswith(".npy") and not fname.endswith(".csv"):
                print("    deleting",os.path.basename(fname))
                os.remove(fname)

    def autoAnalyze(self):
        """call this to make all the graphs and output a HTML report."""
        print("Perfoming full automatic analysis...")
        t1=time.perf_counter()
        self.cleanUp()
        self.figure_rois()
        self.figure_roi_inspect_all()
        self.figure_dGoR_roi(showEach=False,saveAs=self.folderSave+"/avg.png")
        self.figure_dGoR_roi(showEach=True,saveAs=self.folderSave+"/each.png")
        self.index()
        print("analysis completed in %.02f sec"%(time.perf_counter()-t1))

    def index(self,launch=True):
        htmlFile=os.path.abspath(self.folderSave+"/index.html")
        """create saveAs/index.html index file. optionally launch it."""
        html="<h1>SWH2P: TSeries Analysis</h1>"
        html+='<code><b>%s</b></code><br>'%self.folder
        if os.path.exists(self.folder+"/experiment.txt"):
            with open(self.folder+"/experiment.txt") as f:
                html+='<code>%s</code>'%f.read().replace("\n","<br>")
        for fname in sorted(os.listdir(self.folderSave)):
            if not fname.lower()[-3:] in 'jpg,png':
                continue
            html+='<hr><h2>%s</h2>'%fname
            html+='<a href="%s"><img src="%s"></a>'%(fname,fname)
            html+='<br>'*3
        with open(htmlFile,'w') as f:
            print("writing",htmlFile)
            f.write(HTML_TEMPLATE.replace('BODY',html))
        if launch:
            print("launching in web browser")
            webbrowser.open(htmlFile)

class ZSeries:
    def __init__(self,folder):
        """initialize with a Z-stack folder."""
        return

class SingleImage:
    def __init__(self,folder):
        """initialize with a single image folder."""
        return

### INITIATING ANALYSIS FROM OUTSIDE

def index_tseries_single(fname,reanalyze=False,genIndex=True):
    """
    Given the path to a single TSeries folder, process it.
    """
    if not os.path.exists(fname+"/RoiSet.zip"):
        print(fname,"<-- NEEDS ROI!!!!!")
    if not os.path.exists(fname+"/experiment.txt"):
        print(fname,"<-- NEEDS EXPERIMENT TEXT FILE!!!!!")
    if os.path.exists(fname+"/SWH2P/index.html"):
        print(fname,"<-- already indexed")
        indexNeeded=False
    else:
        print(fname,"<-- needs indexing")
        indexNeeded=True
    if indexNeeded or reanalyze:
        print(fname,"<-- analyzing")
        TS=TSeries(fname)
        TS.autoAnalyze()
    if genIndex:
        index_indexes(os.path.dirname(fname))

def index_tseries_all(folder,mustContain=False,reanalyze=False):
    """
    Given a master folder containing a bunch of TSeries folders,
    process each of those TSeries folders. If mustContain is a string, only
    folders with that string in their folder name will be analyzed.
    """
    for fname in sorted(glob.glob(folder+"/TSeries-*")):
        if mustContain and not mustContain in fname:
            print(fname,"<-- skipping")
        else:
            index_tseries_single(fname,reanalyze,genIndex=False)
    index_indexes(folder)

def index_indexes(folder,saveAs="index2.html"):
    """
    given a master folder, find all '/SWH2P/index.html' files and create
    a master index to them.
    """
    indexes=[]
    saveAs=os.path.abspath(os.path.join(folder,saveAs))
    for subFolder in glob.glob(folder+"/*/"):
        if os.path.exists(subFolder+"/SWH2P/index.html"):
            indexes.append(os.path.abspath(subFolder+"/SWH2P/index.html"))

    html='<html><body><h1>Automatic Index</h1><ul>'
    for item in sorted(indexes):
        html+='<li><a href="%s">%s</a>'%(item,
            os.path.basename(os.path.dirname(os.path.dirname(item))))
    html+='</ul></body></html>'
    with open(saveAs,'w') as f:
        f.write(html)
        print("saved",saveAs)
    webbrowser.open(saveAs)

if __name__=="__main__":
    print("DO NOT RUN THIS DIRECTLY")

    TS=TSeries(r'C:\Users\swharden\Documents\temp\TSeries-01112017-1536-1177')
    #TS.autoAnalyze()