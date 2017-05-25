# ROI Analysis Pipeline
This collection of scripts aids in the automated analysis of large collections of TIFs (most likely fluorescent micrographs), taking ROI data (from FIJI/ImageJ), and reporting it as delta F/F. Additional tools are included which assist in the creation of video. An ultimate goal of this type of analysis is to provide a web-accessable front-end to the data immediately after it is acquired.

## Workflow
To use these tools, acquire and analyze data in these steps

* use Micro-Manager to image video (saving output as individual TIFs)
* load the video (stack) into ImageJ and define ROIs with the ROI tool
* save the ROI file as a zip in the same folder as the TIF (filename.zip)
* use ImageJ's multi-measure to create filename.csv
* use the R script to create filename.csv.dff.csv
* use the python script to draw graphs from the "dff" file over the original images

## Example Output

* https://www.youtube.com/watch?v=EEuXCMoRtsw
* https://www.youtube.com/watch?v=1OHvPi1TbII

# Delta F/F Theory

![doc/theory.jpg](doc/theory.jpg)