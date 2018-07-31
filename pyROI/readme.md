# GCaMP6f Analysis

## Folder Arrangement
There is a master experiment folder. This this example it is:
```
X:\Data\AT1-Cre\MPO GCaMP6f\data
```
The master folder probably contains an index.php. Copy/paste this into the master folder as necessary to utilize the lab website. A demo [`index.php`](index.php) is provided. For convenience, I also store a [default ROI set](RoiSet-default.zip) in this location.

Inside the master folder are sub-folders, one for each different slice analyzed:
```
...
X:\Data\AT1-Cre\MPO GCaMP6f\data\18-03-30-animal3-slice1
X:\Data\AT1-Cre\MPO GCaMP6f\data\18-03-30-animal3-slice2-los
X:\Data\AT1-Cre\MPO GCaMP6f\data\18-03-30-animal3-slice3
...
```

Every slice folder must have a `video` subfolder, and inside it are individual TIFs with filenames corresponding to the epoch time of its acquisition. These file names must be named this way, otherwise acquisition time is unreliable. (Note that acquisition time is NOT the file save time).

```
...
X:\Data\AT1-Cre\MPO GCaMP6f\data\18-03-30-animal3-slice1\video\1522426698.995.tif
X:\Data\AT1-Cre\MPO GCaMP6f\data\18-03-30-animal3-slice1\video\1522426720.769.tif
X:\Data\AT1-Cre\MPO GCaMP6f\data\18-03-30-animal3-slice1\video\1522426742.589.tif
X:\Data\AT1-Cre\MPO GCaMP6f\data\18-03-30-animal3-slice1\video\1522426764.399.tif
...
```

## Running Experiments

Create a sub-folder in the master folder for each run. Date it appropraitely. It must contain the word _animal_ in the folder name. Ideally it is of the format `18-07-30-animal2-slice2`.

Use Scott's Micro-Manager (ImageJ) plugin to acquire video. Frames are labeled with the time of image capture. At the end of the experiment, save the video as an image sequence in the `video/` folder inside the sub-folder created for this slice. Ensure to select  _use frame labels as file names_ so the filename contains the image capture time.

Create an `experiment.txt` file in every sub folder. Describe what you did for each experiment, as well as what animal was used.

## Analyzing Data

### Software Setup
* For acquisition 
  * Use micro-manager (https://micro-manager.org)
  * Use the [SWHLab2.ijm](https://github.com/swharden/micro-manager-plugins/blob/master/plugin/SWHLab2.ijm) plugin for video acquisition with TTL light source control
* Analysis requires FIJI
  * Use FIJI (https://fiji.sc), which I refer to as ImageJ.
  * Before using it select "Analyze", "set measurements", and only select "mean".
* Analysis requires Python
  * I use [Anaconda](https://www.anaconda.com/download/) (Python 3.6.1)

### Define and Measure ROIs
Before automatic analysis can occur, ROIs must be defined and saved. This must be done individually for every slice folder.

* delete any images in `video/` which don't have the proper filename
* drag/drop a cell's `video/` folder onto ImageJ
* drag/drop the [default ROI set](RoiSet-default.zip) onto ImageJ
* check the "show all" box to simplify your life
* Place the first ROI (the big one) over _background_ which does not change with drug
* Place every other ROI over whatever you intend to measure
* Select all ROIs (critically important), press "More", select "Save"
* Save in the root slice folder (not the video folder) as `RoiSet.zip`
* Press "More", select "multi-measure".
* Save the output in the root slice folder (not the video folder) as `Results.xls` (not CSV)
* Close all FIJI images and close the ROI window.
* Repeat until all slice folders have `RoiSet.zip` and `Results.xls`.

### Create Graphs and Videos

### Batch Script
I usually create a batch script to launch Python me and give my scripts the correct arguments. An example analysis batch file is [`analyze_folder.bat`](analyze_folder.bat).
