# this is an example program using the boshROI package
########################################################

# clear the workspace
# this helps force re-loading of code which may have been changed elsewhere.
rm(list = ls())

### LOAD THE PACKAGE FROM THE SORUCE RATHER THAN BUILDING IT AND INSTALLING IT
# none of this is required if you just install the package like a regular person
# but installing is slow and you don't want to do it every time you make a change
# you are not required to setwd() which makes everything easier
# first we need to determine the path of this script
if(class(try(sys.frame(1)$ofile)) == "try-error") {
  # this works from a console
  message("assuming we are in a console")
  thisScript.dir <- getwd()
} else {
  # this works in RStudio
  message("assuming we are in RStudio")
  thisScript.dir <- dirname(sys.frame(1)$ofile)
}
message("this script lives in: ",thisScript.dir)
boshPackage.dir <- paste(thisScript.dir,"../../../../boshROI") # tell it where boshROI package is
boshPackage.dir <- normalizePath(boshPackage.dir) # turn it into an absolute file path
boshPackage.dir <- gsub("\\\\", "/", boshPackage.dir)
demoCellData.dir <- normalizePath(paste(boshPackage.dir,"../data/cell1",sep="/"))
message("documenting package in: ",boshPackage.dir)
library(devtools)
devtools::document(boshPackage.dir)
message("loading package from: ",boshPackage.dir)
devtools::load_all(boshPackage.dir, recompile = TRUE, reset = TRUE)

######################################################################
### HERE IS WHERE YOU WRITE A SMALL PROGRAM WHICH USES THE PACKAGE ###
######################################################################

#demoCellData.dir<-"X:/Data/SCOTT/2017-05-10 GCaMP6f/GCaMP6f PFC OXTR cre/2017-06-01 cell3"
ROI<-newRoiFolder(demoCellData.dir, framePeriod=10, firstRoiBaseline=FALSE)

# make some figures to be shown
plot_ROI_DFF(ROI)
plot_ROI_RAW(ROI)

# make some figure to be saved
plot_ROI_DFF(ROI, saveAs=paste(thisScript.dir,"dff.png",sep="/"))
plot_ROI_RAW(ROI, saveAs=paste(thisScript.dir,"raw.png",sep="/"))