# ROI Analysis Pipeline
This collection of scripts aids in the automated analysis of large collections of TIFs (most likely fluorescent micrographs), taking ROI data (from [FIJI/ImageJ](https://fiji.sc/)), and reporting it as delta F/F. Additional tools are included which assist in the creation of video. These scripts can also be integrated with [SWHLabPHP](https://github.com/swharden/SWHLabPHP) to yield a web-accessable front-end to the data immediately after it is acquired.

![](doc/theory.jpg)

# Example Output

## Figures
![](doc/graphs/fig_traces.png)
![](doc/graphs/fig_av.png)

## Web Interface
![](doc/graphs/screenshot.png)

## Video
![](Python/video_frame_02400.png)
* https://www.youtube.com/watch?v=EEuXCMoRtsw
* https://www.youtube.com/watch?v=1OHvPi1TbII

# Workflow
This is a work in progress, but as of now the workflow is:

* 1 video experiment = 1 folder. Folder name format is like `2017-05-23 cell2`
* use Micro-Manager to image video (saving output as individual TIFs in this folder)
* this folder will also contain:
  * `experiment.txt` made by hand at the time of image acquisition
  * `RoiSet.zip` made with ImageJ
  * `Results.xls` made with ImageJ multi-measure
* Data analysis scripts:
  * `Results.xls` will always have mean pixel values for each ROI
  * `Results_B.xls` will contain (identically formatted) dF/F calculated by Beronica (R)
  
## Photobleach Compensation
To counteract photobleaching, the first ROI will always be of a non-responsive cell or area. Every subsequent ROI will have the first ROI subtracted from it. 

## experiment.txt
This is an example of how to make an experiment.txt at the time of recording noting important information
```
GABA Cre / GCaMP6f injection / mPFC
# some cool note
baseline=100-120
TGOT=123-234
antagonist=50-300
```
