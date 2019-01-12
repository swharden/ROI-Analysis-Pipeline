"""
code related to inspection of TSeries
(loading of folder images, reading XML, etc)
"""

import numpy as np
import matplotlib.image as mpimg
import glob
import os

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
        return False
    else:
        val=xml.split(match)[1].split("value=",3)[matchNumber]
        val=val.split('"')[1]
    try:
        val=float(val)
    except:
        val=str(val)
    return val

def xml_parse_prairie(xmlFileName):
    """
    given the path to a TSeries XML file from prairie,
    parse it and return a dictionary with the useful info.
    """
    xmlFileName=os.path.abspath(xmlFileName)
    print("parsing",xmlFileName)
    assert os.path.exists(xmlFileName)

    with open(xmlFileName) as f:
        xml=f.read()
        xml=xml.split(">")
        for i,line in enumerate(xml):
            xml[i]=line.strip()
        xml="".join(xml)
    conf={}
    for key in ['opticalZoom','objectiveLens', # physical lens
                'pixelsPerLine','linesPerFrame', # dimensions
                'dwellTime','framePeriod','scanLinePeriod' # laser pixel timing
                'laserPower', # laser settings
                'pmtGain~1~','pmtGain~2~', # PMT settings
                ]:
        conf[key.replace("~",'')]=xml_value_from_key(xml,key)
    for key in sorted(conf.keys()):
        print("XML parsing produced: [%s]=%s"%(key,conf[key]))

    times=[float(x.split('"')[1]) for x in xml.split("absoluteTime=")[1:]]
    conf["times"]=np.array(times)
    print("XML parsing produced: %d time points"%len(times))
    return conf

def inspect_folder(folder):
    """
    Given a 2P folder right off the 2P scope, load all the image data
    and it (as two numpy arrays) plus a dictionary of XML settings (i.e.,
    magnification, scan rate, laser settings, etc.)

    Returns [G,R,fnamesCH1,fnamesCH2,conf]
    """

    assert os.path.exists(folder)
    matches=glob.glob(folder+"/*.xml")
    fnamesCH1=sorted(glob.glob(folder+"/*_Ch1_*.tif"))
    fnamesCH2=sorted(glob.glob(folder+"/*_Ch2_*.tif"))
    print(matches)
    assert len(matches)==1
    conf=xml_parse_prairie(matches[0])

    sizeX=conf['pixelsPerLine']
    sizeY=conf['linesPerFrame']
    times=conf['times']
    nFrames=len(times)

    if os.path.exists(folder+"/data_G.npy"):
        print("loading data from disk...")
        G,R=np.load(folder+"/data_G.npy"),np.load(folder+"/data_R.npy")
    else:
        R,G=np.empty((nFrames,sizeY,sizeX)),np.empty((nFrames,sizeY,sizeX))
        for i,timePoint in enumerate(times):
            print("loading frame %d of %d (%.02f%%)"%(i+1,len(times),(i+1)*100.0/len(times)))
            R[i]=mpimg.imread(fnamesCH1[i])
            G[i]=mpimg.imread(fnamesCH2[i])
        print("saving data to disk...")
        np.save(folder+"/data_G.npy",G)
        np.save(folder+"/data_R.npy",R)
    print("time series data is in memory and ready to process!")
    return [G,R,fnamesCH1,fnamesCH2,conf]

if __name__=="__main__":
    print("##### DO NOT RUN THIS SCRIPT DIRECTLY #####")
    fldr=r'C:\Users\swharden\Documents\temp\TSeries-01112017-1536-1177'
    inspect_folder(fldr)
    print("DONE")