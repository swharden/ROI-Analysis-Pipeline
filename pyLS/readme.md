# pyLineScan
pyLineScan is a Python module intended to make it easy to access, analyze, and display data from PrairieView linescan folders. When the`LineScan` class is initialized with a path to a linescan folder, it automatically scans the folder for linescan images and reads the XML and ENV files to determine their framerate. Vertically-averaged traces of red, green, and delta(green/red) are immediately available. Plotting functions exist as well to rapidly visualize the experiment performed. These scripts are a sandbox of experimental code maintained by Scott Harden.

# Example Usage
To generate figures and CSV files for a LineScan folder, just create 

```Python
import pyLineScan
LS=PyLineScan.LineScan('/path/to/LineScan/')
LS.allFigures()
```

## Real Data Output Folders 
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
