# pyLineScan
pyLineScan is a Python module intended to make it easy to access, analyze, and display data from PrairieView linescan folders. When the`LineScan` class is initialized with a path to a linescan folder, it automatically scans the folder for linescan images and reads the XML and ENV files to determine their framerate. Vertically-averaged traces of red, green, and delta(green/red) are immediately available. Plotting functions exist as well to rapidly visualize the experiment performed. These scripts are a sandbox of experimental code maintained by Scott Harden.

### Features
* **Automatic configuration** detection is achieved by reading [ENV](../data/linescan/realistic/LineScan-06162017-1223-628/LineScan-06162017-1223-628.env) and [XML](../data/linescan/realistic/LineScan-06162017-1223-628/LineScan-06162017-1223-628.xml) files to pull laser and scan configuration data. This is especially useful for determining the time axis of a linescan image (scan line period).
* **Automatic feature detection** selects the brightest struture in a linescan (using the red channel) and sets the marks around its brightest area (until the intensity reaches 25% of peak intensity). This eliminates the need to manually define structures of interest.
* **1D gaussian data smoothing** (in the time domain) creates less noisy data. This would presumably be equivocal to increasing the dwell time and reducing the number of scans over the same duration, but this can be done off-line and adjusted as desired for analysis.
* **Automatic figure creation** is simple since most LineScans are analyzed for the same things. Pre-programmed figures are included in the core class and figures can be generated with minimal effort.
* **Automatic CSV file output** saves red (data_R.csv), green (data_G.csv), green/red (data_GoR.csv), and baseline-subtracted delta green/red (data_dGoR.csv) automatically for every linescan analyzed. These CSV files are ready to copy/paste into another analysis suite such as Matlab or OriginLab.

## Usage

### Within Python

#### Quickstart
```Python
import pyLineScan
LS=PyLineScan.LineScan('/path/to/LineScan/')
LS.allFigures()
```
#### Optional Arguments
To generate figures and CSV files for a LineScan folder, just create an `LineScan` class instance by feeding it the path to the LineScan folder. A few optional arguments are included here. See the library documentation for details.
```python
LineScan(folder,baseline=[1,2]) #manually defines the baseline region as between 1 and 2 seconds
LineScan(folder,marks=None) #bypasses automatic feature detection, markers to pixels 10 and 20
LineScan(folder,sigma=10) #applies a 10 pixel horizontal gaussian blur to the image to smooth its data
```

### Launching from Command Line

Give it a single argument - the path to a 2P LineScan folder right off the microscope:
```bash
python analyze_project.py "/path/to/LineScan"
```

I prefer creating a batch file with full file paths, something like:
```bash
"C:\Users\swharden\AppData\Local\Continuum\Anaconda3\python.exe" "C:\Users\shengwanhui\Documents\GitHub\ROI-Analysis-Pipeline\pyLS\analyze_project.py" "X:\Data\SD\PVN mannital\07-09-2018 lactating rat PVN\07-16-2018 MCN MT 2P\18723030"
pause
```

A sample batch file is provided: [analyze_project.bat](analyze_project.bat)

## Sample Output

### Sample Data Output Folders 
* [LineScan-06092017-1414-619](../data/linescan/realistic/LineScan-06092017-1414-619/analysis) <-- single linescan
* [LineScan-06092017-1414-620](../data/linescan/realistic/LineScan-06092017-1414-620/analysis) <-- single linescan
* [LineScan-06092017-1414-621](../data/linescan/realistic/LineScan-06092017-1414-621/analysis) <-- single linescan
* [LineScan-06092017-1414-622](../data/linescan/realistic/LineScan-06092017-1414-622/analysis) <-- single linescan
* [LineScan-06092017-1414-623](../data/linescan/realistic/LineScan-06092017-1414-623/analysis) <-- single linescan
* [LineScan-06162017-1223-628](../data/linescan/realistic/LineScan-06162017-1223-628/analysis) <-- repeated linescans
* [LineScan-06162017-1223-636](../data/linescan/realistic/LineScan-06162017-1223-628/analysis) <-- repeated linescans

### Sample Data Output Figures (LineScan-06162017-1223-636)
![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_01_img.png)
![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_02_avg.png)
![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_03_drift1.png)
![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_04_drift2.png)
