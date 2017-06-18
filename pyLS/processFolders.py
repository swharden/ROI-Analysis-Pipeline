from pyLineScan import LineScan
import glob
import os
from PIL import Image
import matplotlib.pyplot as plt
import datetime

def analyzeSubfolders(folderParent,overwrite=False):
    """
    given a parent directly, perform automated linescan analysis on all sub-folders.
    Output data is saved in each linescan folder's 'results' sub-folder.
    """
    folderParent=os.path.abspath(folderParent)
    print("analyzing all linescans in",folderParent)
    linescanFolders=sorted(os.listdir(folderParent))
    for i,name in enumerate(linescanFolders):
        if not name.startswith("LineScan-"):
            continue
        folderLinescan=os.path.join(folderParent,name)
        print("PROCESSING LINESCAN %d OF %d: %s"%(i+1,len(linescanFolders),name))
        folderOutput=os.path.join(folderLinescan,"analysis")
        if not os.path.exists(folderOutput):
            os.mkdir(folderOutput)
        if overwrite or not os.path.exists(os.path.join(folderOutput,"fig_01_img.png")):
            print(" analyzing linescan data...")
            LS=LineScan(folderLinescan,baseline=None)
            LS.allFigures()
            plt.close('all')
        if overwrite or not os.path.exists(os.path.join(folderOutput,"ref.png")):
            refFigures=glob.glob(folderLinescan+"/References/*Window2*.tif")
            if len(refFigures):
                print(" generating reference figure...")
                im=Image.open(refFigures[0])
                im.save(os.path.join(folderOutput,"ref.png"))

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
    out+="<b style='font-size: 300%%'>boshLS</b><br><i>automatic linescan index generated at %s</i><hr><br>"%timestamp
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
        out+="<br>"*6
    out+="</code></body></html>"
    fileOut=os.path.abspath(folderParent+"/index.html")
    with open(fileOut,'w') as f:
        f.write(out)
    print("saved",fileOut)


if __name__=="__main__":
    #folderParent='../data/linescan/realistic/'
    folderParent=r'X:\Data\SCOTT\2017-06-16 OXT-Tom\2p'
    analyzeSubfolders(folderParent,overwrite=False)
    index(folderParent)
    print("DONE")