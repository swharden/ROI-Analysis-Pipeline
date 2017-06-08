# this is an example program using the boshROI package
########################################################

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
print("thisScript.dir")
print(thisScript.dir)
boshPackage.dir <- paste(thisScript.dir,"../../../../boshROI") # tell it where boshROI package is
boshPackage.dir <- normalizePath(boshPackage.dir) # turn it into an absolute file path
boshPackage.dir <- gsub("\\\\", "/", boshPackage.dir)
message("documenting package in: ",boshPackage.dir)
devtools::document(boshPackage.dir)
message("loading package from: ",boshPackage.dir)
library(devtools)
load_all(boshPackage.dir)

######################################################################
### HERE IS WHERE YOU WRITE A SMALL PROGRAM WHICH USES THE PACKAGE ###
######################################################################

# pick a ROI folder you want to analyze
roi_folder_path<-"X:/Data/SCOTT/2017-05-10 GCaMP6f/GCaMP6f PFC OXTR cre/2017-06-01 cell3"

# this is how you create a RoiFolder class.
# just give it some info and it will do all the work reading the files
# delta F / F is calculated automatically too.
ROI<-newRoiFolder(roi_folder_path, framePeriod=10, firstRoiBaseline=FALSE)
# now that the class is loaded, you can 


# this is how you create a simple graph (which is displayed by default)
plot_ROI_DFF(ROI)

# if the "saveAs" argument is given, the graph will be saved instead of displayed
plot_ROI_DFF(ROI,saveAs=paste(thisScript.dir,"output.png",sep="/"))