"""
Code in this file aims to automatically produce "difference images" from 
full frame micrographs of calcium-sensitive fluorophores before and after a drug
is applied. This is done by creating a baseline image (the average of several
TIFs before the drug) and calculating the difference between that and the average
image of the drug exposure. The difference is color-coded where no change is white,
decrease in brightness is blue, an dincrease in brightness is red.
"""
import numpy as np
import glob
from matplotlib import pyplot as plt
import os

class Drug:
    def __init__(self, drugName, frameAdded, durationFrames = 10, padFrames = 1):
        """The Drug class helps associate a drug's name with its baseline and data frame numbers."""
        frameBaseline1 = frameAdded - padFrames - durationFrames
        frameBaseline2 = frameAdded - padFrames
        frameDrug1 = frameAdded + padFrames
        frameDrug2 = frameAdded + padFrames + durationFrames
        self.drugFrame = frameAdded
        self.drugName = drugName
        self.frames = [frameBaseline1, frameBaseline2, frameDrug1, frameDrug2]

def imageSequenceAverageData(folderPath, frameFirst=None, frameLast=None):
    """
    Given a folder of images which contribute to a video, create a numpy array representing 
    the average pixel intensity of every image which lies between the given frame numbers.
    """

    # determine which image files in the folder will be analyzed
    imageFiles = sorted(glob.glob(folderPath+"/*.tif"))
    if frameFirst==None:
        frameFirst = 0
    if frameLast==None:
        frameLast = len(imageFiles)-1
    print(f"creating average image data from images {frameFirst} - {frameLast} (of {len(imageFiles)})")

    # Get dimensions from the first image
    firstImageData = plt.imread(imageFiles[frameFirst])
    width, height = firstImageData.shape
    print(f"populating array to match first image size: {width} x {height}")

    # create a 2D array to hold the SUM of all image data
    dataSum = np.zeros((width, height))

    # add each image's pixel values to the data
    imageFilesToAnalyze = imageFiles[frameFirst:frameLast]
    for i, fname in enumerate(imageFilesToAnalyze):
        imgData = plt.imread(fname)
        dataSum += imgData
    
    # create the average image for this data
    dataAverage = dataSum/len(imageFilesToAnalyze)

    return dataAverage

def imageDataDisplay(data, title=None, saveAs=None):
    """
    Given a 2D image delta dataset (where value 0 represents no change), 
    create a plot where negative/positive is blue/red and save or show it.
    """

    # the axis limits (blue and red) are a function of standard deviation
    LMT = np.std(data)*5
    print(f"image data limit: +/- {LMT}")
    
    # place the 2d image data into a figure
    plt.figure(figsize = (12,8))
    plt.imshow(data, 'bwr', clim=(-LMT, LMT))
    plt.colorbar(extend = 'both')
    plt.title(title)
    plt.tight_layout()

    # if a filename is given, save the figure as that filename
    if saveAs:
        plt.savefig(saveAs, dpi=150)
    else:
        plt.show()
    plt.close()
    return

def imageDelta(folderPath, frames=[5, 10, 15, 20], title="", saveAs=None):
    """
    Given a video folder (folder containing many TIFs), use the frame numbers
    to create an average baseline image and an average drug image. Then create
    a numpy array depicting the difference between these images. Next, display
    or save the image.
    """
    imgBaseline = imageSequenceAverageData(folderPath, frames[0], frames[1])
    imgDrug = imageSequenceAverageData(folderPath, frames[2], frames[3])
    imgDiff = imgDrug - imgBaseline
    title += f" ([{frames[0]}:{frames[1]}] to [{frames[2]}:{frames[3]}])"
    imageDataDisplay(imgDiff, title, saveAs)
    return

def imageSeriesIntensityByFrame(folderPath):
    """Given a video folder, return an array of intensity for each frame."""
    imageFiles = sorted(glob.glob(folderPath+"/*.tif"))
    intensities = np.full(len(imageFiles), np.nan)
    for i, fname in enumerate(imageFiles):
        intensity = np.average(plt.imread(fname))
        intensities[i] = intensity
        print("image %d of %d intensity %.02f"%(i+1, len(imageFiles), intensity))
    return intensities

def graphDrugExperiment(drugs, folderPath):
    """
    Given a video folder, create a graph of intensity for each frame.
    Also use an array of drugs to shade baseline and measurement regions.
    """

    # type checks
    assert os.path.exists(folderPath)
    assert len(glob.glob(folderPath+"/*.tif"))>100
    assert isinstance(drugs, list)
    for drug in drugs:
        assert isinstance(drug, Drug)
    parentFolder = os.path.dirname(folderPath)

    # create time course graph
    intensities = imageSeriesIntensityByFrame(folderPath)
    plt.figure(figsize=(10, 6))
    for i,drug in enumerate(drugs):
        color = "C%d"%i
        lbl = drug.drugName + " (frame %d)"%drug.drugFrame
        plt.axvspan(drug.frames[0], drug.frames[1], color = color, alpha=.1, lw=0)
        plt.axvspan(drug.frames[2], drug.frames[3], color = color, alpha=.3, lw=0, label = lbl)
    plt.plot(intensities, '.-', color='k', label="full frame intensity")
    plt.ylabel("Intensity (AFU)")
    plt.xlabel("Frame Number")
    plt.tight_layout()
    plt.legend()
    imgFname = os.path.abspath(parentFolder+"/analysis_01_intensityOverTime.png")
    plt.savefig(imgFname)
    plt.close()
    print("Saved", imgFname)

    # create an intensity change image for every drug application
    for i,drug in enumerate(drugs):
        assert isinstance(drug, Drug)
        imgFname = os.path.abspath(parentFolder+"/analysis_%02d_%s.png"%(i+2, drug.drugName))
        imageDelta(folderPath, drug.frames, drug.drugName, imgFname)
        plt.close()
        print("Saved", imgFname)

    return

def drugFrameFromFileList(timeMinutes, folderPath):
    """
    Given a video folder (where TIFs are named based on acquisition time), return
    the frame number of the first image that occurs after the given time.
    """
    fnames = sorted(glob.glob(folderPath+"/*.tif"))
    fnames = [os.path.basename(x) for x in fnames]
    fnames = [x.lower().replace(".tif",'') for x in fnames]
    fnames = [float(x) for x in fnames]
    times = np.array(fnames)
    times = times - times[0]
    timesMin = times / 60
    drugFrame = -1
    for i, timeMin in enumerate(timesMin):
        if timeMin >= timeMinutes:
            drugFrame = i
            break
    print(f"Drug at {timeMinutes} minutes is frame #{drugFrame}")
    return drugFrame

def ensureImageFilenamesAreNumbers(videoFolder):
    """
    Run this to verify all video TIFs use filenames which can be converted to
    floating point numbers. Do this up-front to prevent a crash half-way through
    the execution of this program.
    """
    print("Verifying filenames in:", videoFolder)
    try:
        for fname in sorted(glob.glob(videoFolder+"/*.tif")):
            fname = os.path.basename(fname)
            fname = fname.replace(".tif","")
            fnameFloat = float(fname)
    except:
        raise Exception("BAD FILENAME IN "+videoFolder)