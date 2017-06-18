# pyLineScan
pyLineScan is a Python module intended to make it easy to access, analyze, and display data from PrairieView linescan folders. When the`LineScan` class is initialized with a path to a linescan folder, it automatically scans the folder for linescan images and reads the XML and ENV files to determine their framerate. Vertically-averaged traces of red, green, and delta(green/red) are immediately available. Plotting functions exist as well to rapidly visualize the experiment performed. These scripts are a sandbox of experimental code maintained by Scott Harden.

## Usage
```python
from pyLineScan import LineScan # import the LineScan class directly from the module
LS=LineScan('/path/to/folder/',baseline=[1.5,2]) # init with a linescan folder and baseline
print(LS.traceG[0]) # shows green values from first linescan
LS.figureDual("demo.png") # makes a plot like the one you see below
```

## Core Class Properties
* configuration data
  * ```LS.frames``` - number of frames in the linescan
  * ```LS.Xs``` - time units for each trace (seconds)
* image data (1d list organized by frame)
  * ```LS.dataR[frame]```
  * ```LS.dataG[frame]```
  * ```LS.dataGoR[frame]```
* marks (m1 and m2 are the pixel values defining the bounds of the structure to be analyzed)
  * ```LS.m1```
  * ```LS.m2```
* trace data (flattened image data of the selected range between the marks)
  * ```LS.traceG[frame]```
  * ```LS.traceR[frame]```
  * ```LS.traceGoR[frame]```
* baseline values
  * ```LS.baselines[frame]```
* baseline-subtracted trace data (delta trace)
  * ```LS.dG[frame]```
  * ```LS.dR[frame]```
  * ```LS.dGoR[frame]```
* average of all traces
  * ```LS.AVGdGoR[frame]```

## Processing Multiple Folders
[processFolders.py](processFolders.py) is a script to automatically generate a linescan graph for every linescan found in a folder. Now they can be easily browsed with a web interface. Convension is that linescan output data is stored in the linescan folder's `./analysis/` folder.

## Screenshot
![](screenshot.png)
