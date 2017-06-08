# this is an example program using the boshROI package
#####################################################

library(devtools)
library(colorRamps)

load_all("../../boshROI")

roi_folder_path<-"X:/Data/SCOTT/2017-05-10 GCaMP6f/GCaMP6f PFC OXTR cre/2017-06-01 cell3"
ROI<-newRoiFolder(roi_folder_path, framePeriod=10, firstRoiBaseline=FALSE)
plot_ROI_DFF(ROI)
plot_ROI_DFF(ROI,saveAs="04.png")