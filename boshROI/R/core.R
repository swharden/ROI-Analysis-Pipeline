# code here has the primary objects and routines
# used in ROI folder analysis
#####################################################



# create a reference class obect to represent an ROI folder and its analyzed data.
# no information about how to analyze this data belongs here. 
# Just attributes describing the ROI folder.
library(methods)
RoiFolder <- setRefClass("RoiFolder",fields=list(folder="character",
                                                 dataFile="character",
                                                 dataRaw="matrix",
                                                 dataDFF="matrix",
                                                 roiLabels="character",
                                                 timePoints="numeric",
                                                 pictureFiles="character",
                                                 roiSetFile="character",
                                                 experimentFile="character",
                                                 baseline="vector"))




# call this to define a new data folder
# create a new object with all the defaults
# return it so the user can change it before it's analyzed
#' @export
newRoiFolder <- function(folder, framePeriod=1, firstRoiBaseline=TRUE){
  
  # make a new class instance and fill out its file path values
  ROI <- RoiFolder()
  ROI$folder<-folder
  ROI$dataFile<-file.path(ROI$folder,"Results.xls")
  ROI$experimentFile=file.path(ROI$folder,"experiment.txt")
  ROI$roiSetFile=file.path(ROI$folder,"RoiSet.zip")
  
  # normalize all the file paths
  ROI$folder<-normalizePath(ROI$folder)
  ROI$dataFile<-normalizePath(ROI$dataFile)
  ROI$experimentFile<-normalizePath(ROI$experimentFile)
  ROI$roiSetFile<-normalizePath(ROI$roiSetFile)
  
  # load the CSV data, time points, ROI labels
  ROI$dataRaw<-roi_data_load(ROI$dataFile, framePeriod=framePeriod)
  
  # if the first row is a baseline, subtract it from other rows then remove it.
  if (firstRoiBaseline){
    message("subtracting ROI 1 from all the rest ...")
    for (i in (2:ncol(ROI$dataRaw))){
      ROI$dataRaw[,i]=ROI$dataRaw[,i]-ROI$dataRaw[,1] # subtract-out column 1
    }
    ROI$dataRaw <- ROI$dataRaw[,-1:0] # chop off the baseline column
  }
  
  # load and parse the experiment file for baseline range (optional)
  experimentParts<-roi_experiment_load(ROI$experimentFile)
  for (i in (1:nrow(experimentParts))){
    item<-as.vector(experimentParts[i,])
    if (item[1]=="baseline"){
      ROI$baseline=c(as.numeric(item[2]),as.numeric(item[3]))
      message("setting baseline region: ",ROI$baseline[1],"-",ROI$baseline[2])
    }
  }
  if (length(ROI$baseline)==0){
    message("no baseline span found, defaulting to first frame")
    ROI$baseline=c(1,1)
  }
  
  # determine the average over the baseline area for each ROI
  message("calculating baseline values for each ROI ...")
  baselineRows<-(ROI$baseline[1]:ROI$baseline[2])
  roiBaselineAverages <- vector(mode="numeric", length=ncol(ROI$dataRaw))
  for (thisCol in (1:ncol(ROI$dataRaw))){
    roiBaselineAverages[thisCol]<-mean(ROI$dataRaw[baselineRows,thisCol])
  }
  
  # calculate delta(F) by subtracting the baseline average from each roi
  deltaF<-ROI$dataRaw
  for (thisCol in (1:ncol(deltaF))){
    deltaF[,thisCol]<-deltaF[,thisCol]-roiBaselineAverages[thisCol]
  }
  
  # create delta(F)/F by dividing this by the baseline average for each roi
  ROI$dataDFF<-deltaF
  for (thisCol in (1:ncol(ROI$dataDFF))){
    ROI$dataDFF[,thisCol]<-ROI$dataDFF[,thisCol]/roiBaselineAverages[thisCol]
  }
  
  return(ROI)
}
