# pyLineScan
pyLineScan is a Python module intended to make it easy to access, analyze, and display data from PrairieView linescan folders. When the`LineScan` class is initialized with a path to a linescan folder, it automatically scans the folder for linescan images and reads the XML and ENV files to determine their framerate. Vertically-averaged traces of red, green, and delta(green/red) are immediately available. Plotting functions exist as well to rapidly visualize the experiment performed. These scripts are a sandbox of experimental code maintained by Scott Harden.

### Features
* **Automatic configuration** detection is achieved by reading [ENV](../data/linescan/realistic/LineScan-06162017-1223-628/LineScan-06162017-1223-628.env) and [XML](../data/linescan/realistic/LineScan-06162017-1223-628/LineScan-06162017-1223-628.xml) files to pull laser and scan configuration data. This is especially useful for determining the time axis of a linescan image (scan line period).
* **Automatic feature detection** selects the brightest struture in a linescan (using the red channel) and sets the marks around its brightest area (until the intensity reaches 25% of peak intensity). This eliminates the need to manually define structures of interest.
* **1D gaussian data smoothing** (in the time domain) creates less noisy data. This would presumably be equivocal to increasing the dwell time and reducing the number of scans over the same duration, but this can be done off-line and adjusted as desired for analysis.
* **Automatic figure creation** is simple since most LineScans are analyzed for the same things. Pre-programmed figures are included in the core class and figures can be generated with minimal effort.
* **Automatic CSV file output** saves red (data_R.csv), green (data_G.csv), green/red (data_GoR.csv), and baseline-subtracted delta green/red (data_dGoR.csv) automatically for every linescan analyzed. These CSV files are ready to copy/paste into another analysis suite such as Matlab or OriginLab.

### Example Usage
```Python
import pyLineScan
LS=PyLineScan.LineScan('/path/to/LineScan/')
LS.allFigures()
```
### Optional Arguments
To generate figures and CSV files for a LineScan folder, just create an `LineScan` class instance by feeding it the path to the LineScan folder. A few optional arguments are included here. See the library documentation for details.
* `lineScan(folder,baseline=[1,2])` _manually defines the baseline region as between 1 and 2 seconds_
* `lineScan(folder,marks=None)` _bypasses automatic feature detection and sets the markers to Y pixel positions 10 an 20_
* `lineScan(folder,sigma=10)` _applies a 10 pixel horizontal gaussian blur to the image to smooth its data_

## Actual Data Output Folders 
* [LineScan-06092017-1414-619](../data/linescan/realistic/LineScan-06092017-1414-619/analysis)
* [LineScan-06092017-1414-620](../data/linescan/realistic/LineScan-06092017-1414-620/analysis)
* [LineScan-06092017-1414-621](../data/linescan/realistic/LineScan-06092017-1414-621/analysis)
* [LineScan-06092017-1414-622](../data/linescan/realistic/LineScan-06092017-1414-622/analysis)
* [LineScan-06092017-1414-623](../data/linescan/realistic/LineScan-06092017-1414-623/analysis)
* [LineScan-06162017-1223-628](../data/linescan/realistic/LineScan-06162017-1223-628/analysis) <-- best
* [LineScan-06162017-1223-636](../data/linescan/realistic/LineScan-06162017-1223-628/analysis) <-- best

## Example Output Figures (LineScan-06162017-1223-636)
![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_01_img.png)
![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_02_avg.png)
![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_03_drift1.png)
![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_04_drift2.png)
