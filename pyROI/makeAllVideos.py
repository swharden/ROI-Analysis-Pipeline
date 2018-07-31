import glob
import os
import subprocess

def execute(cmd):
    print(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()
    print()

def fnameToTime(path):
    fname=os.path.basename(path)
    fname=fname.split(".")
    thisTime=fname[0]+"."+fname[1]
    return float(thisTime)

def video_tif_to_bmp(folder,brightness=5,recalculate=False):
    assert os.path.exists(folder+"/video/")
    if os.path.exists(folder+"/video2/"):
        if recalculate==False:
            return
        for fname in glob.glob(folder+"/video2/*.*"):
            os.remove(fname)
        os.rmdir(folder+"/video2/")
    os.mkdir(folder+"/video2")
    filesTif=sorted(glob.glob(folder+"/video/*.tif"))
    filesTif=[os.path.abspath(x) for x in filesTif]
    timeStart = fnameToTime(filesTif[0])
    for i in range(len(filesTif)):
        fnameBmp=os.path.abspath(folder+"/video2/video%04d.bmp"%i)
        timeNow=fnameToTime(filesTif[i])
        timeDeltaMins = (timeNow-timeStart)/60.0
        msg = "%s | %.02f min"%(os.path.basename(folder),timeDeltaMins)
        cmd='convert "%s" '%filesTif[i]
        cmd+='-function Polynomial %d,0 '%brightness
        cmd+='-gravity northwest -stroke "#000000" -fill "#FFFF00" '
        cmd+='-weight bold -pointsize 30 -annotate 0 "%s" '%msg
        cmd+='-append "%s"'%fnameBmp
        execute(cmd)

def video_create_mp4(folder,recalculate=False):
    if os.path.exists(folder+"/video.mp4"):
        if recalculate==False:
            return
        os.remove(folder+"/video.mp4")
    assert os.path.exists(folder+"/video2/")
    pathIn=os.path.abspath(folder+"/video2/video%04d.bmp")
    fileOut=os.path.abspath(folder+"/video.mp4")
    cmd = 'ffmpeg.exe -framerate 10 -y -i "%s" '%pathIn
    cmd += '-c:v libx264 -pix_fmt yuv420p "%s" '%fileOut
    execute(cmd)

if __name__=="__main__":
    recalculate=False
    for path in (os.listdir("./")):
        if os.path.isdir(path):
            if os.path.exists(path+"/video.mp4") and recalculate==False:
                print(path," - already analyzed")
            else:
                print(path," - ### ANALYZING NOW ###")
                video_tif_to_bmp(path,recalculate=recalculate)
                video_create_mp4(path,recalculate=recalculate)
    print("DONE")