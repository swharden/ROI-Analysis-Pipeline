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
* Analysis requires
  * Python - I suggest [Anaconda](https://www.anaconda.com/download/)
  * FFMPG - [Windows builds page](https://ffmpeg.zeranoe.com/builds/) ([main website](https://www.ffmpeg.org))
  
### Define and Measure ROIs
Before automatic analysis can occur, ROIs must be defined and saved. This must be done individually for every slice folder.

* delete any images in `video/` which don't have the proper filename
* drag/drop a cell's `video/` folder onto ImageJ
* drag/drop the [default ROI set zip](RoiSet-default.zip) onto ImageJ (drag/drop the zip file itself)
* check the "show all" box to simplify your life
* While moving ROIs, be careful only to drag them and never to resize them
* Place the first ROI (the big one) over _background_ which does not change with drug
* Place every other ROI over whatever you intend to measure
* Select the ROI window, Select all ROIs with CTRL+A, press "More", select "Save"
* Save in the root slice folder (not the video folder) as `RoiSet.zip`
* I often screenshot the window (showing all the squares) and save it as `RoiSet.png` in the same folder
* Press "More", select "multi-measure", and accept the default checkboxes
* If columns other than "mean" are created, click "analyze", "set measurements", and only select "mean"
* Save the output in the root slice folder (not the video folder) as `Results.xls` (not CSV)
* Close all FIJI images and close the ROI window.
* Repeat until all slice folders have `RoiSet.zip` and `Results.xls`

### Create dF/F Graphs
This part is optional, since `Results.xls` saved in the previous step could be imported directly into Origin. However, the end of this script updates an XLS file in the root experiment folder to produce a large XLS file with one column per slice (pulling in each slice's individual results file), so this section may be desired so the output XLS could be imported to Origin.

* Launch the [makeAllGraphs.py](makeAllGraphs.py) script with the path to the high-level experiment folder as its only argument. 
* This usually runs very fast and can be run routinely
* This could be launched with a batch script (I suggest adding a `pause` command at the end).
* To re-render a slice's graphs:
  * Delete `dataAvg.csv` and `dataRaw.csv` from the slice folder
  * Delete the `swhlab` folder in the slice folder

```bash
"C:\path\to\python.exe" "C:\path\to\makeAllGraphs.py" "X:\Data\AT1-Cre\MPO GCaMP6f\data"
```

### Create Annotated Video
This part is extremely optional. Video is only useful for experiment inspection on the website, or to produce an occasional clip for a powerpoint file.

* Just like the previous python script, run this one with the master path as a single argument.
* This usually runs **very slow** and should be run carefully
* This could be launched with a batch script (I suggest adding a `pause` command at the end).
* Brightness can be tweaked by editing the `brightness=` line at the bottom of the script
* To re-render a slice's video (such as after modifying brightness):
  * Delete the `video.mp4` file in the slice folder
  * Delete the `video2` folder in the slice folder
  * Re-run the Python script

```
"C:\path\to\python.exe" "C:\path\to\makeAllVideos.py" "X:\Data\AT1-Cre\MPO GCaMP6f\data"
```

To customize brightness, add an extra argument. The default is 10.

```
"C:\path\to\python.exe" "C:\path\to\makeAllVideos.py" "X:\Data\AT1-Cre\MPO GCaMP6f\data" 20
```

### Viewing Experiments on the Website
Since the folder architecture is highly defined, an [`index.php`](index.php) has been created to browse the experiment folder. If you have multiple experiment folders, drop [`index.php`](index.php) in the root of each folder and navigate to that folder on the website.

* The X-drive folder structure can be accessed via [http://192.168.1.9/X/](http://192.168.1.9/X/)
