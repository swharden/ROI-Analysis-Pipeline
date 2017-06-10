from pyLineScan import LineScan
import glob
import os
from PIL import Image

def analyzeSubfolders(folderParent):
    """
    given a parent directly, perform automated linescan analysis on all sub-folders.
    Output data is saved in each linescan folder's 'results' sub-folder.
    """
    folderParent=os.path.abspath(folderParent)
    print("analyzing all linescans in",folderParent)
    linescanFolders=sorted(os.listdir(folderParent))
    for i,name in enumerate(linescanFolders):
        folderLinescan=os.path.join(folderParent,name)
        print("PROCESSING LINESCAN %d OF %d: %s"%(i+1,len(linescanFolders),name))
        folderOutput=os.path.join(folderLinescan,"analysis")
        if not os.path.exists(folderOutput):
            os.mkdir(folderOutput)
        if not os.path.exists(os.path.join(folderOutput,"fig_swh_dual.png")):
            print(" analyzing linescan data...")
            LS=LineScan(folderLinescan)
            LS.figureDual(os.path.join(folderOutput,"fig_swh_dual.png"))
        if not os.path.exists(os.path.join(folderOutput,"ref.png")):
            refFigures=glob.glob(folderLinescan+"/References/*Window2*.tif")
            if len(refFigures):
                print(" generating reference figure...")
                im=Image.open(refFigures[0])
                im.save(os.path.join(folderOutput,"ref.png"))

if __name__=="__main__":
    analyzeSubfolders('../data/linescan/realistic/')
    print("DONE")