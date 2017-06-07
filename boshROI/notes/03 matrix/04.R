# Notes related to objects

# given a tab-separated file (like Results.xls), return its data as a matrix.
# row names are the time (in seconds) of the data.
roi_data_load <- function(fname, framePeriod=1){
  message("loading raw data from ",fname)
  rawData <- as.matrix(read.csv(fname, sep="\t"))
  rawData <- rawData[,-1:0] # chop off the first column (frame number)
  frameTimes <- (1:nrow(rawData))-1 # ascending numbers starting at 0
  frameTimes <- frameTimes * framePeriod # adjust for frame period
  rownames(rawData) <- frameTimes # set row names as frame period
  return(rawData)
}

# returns a matrix where every row is a line in the experiment text file.
# if the line has 3 valid field, it's a range (i.e., a span of drug)
# if the line has 2 valid field, it's a point (i.e., time of bubble blip)
# if the line has 1 valid field, it's just a comment
roi_experiment_load <- function(fname){
  message("loading experiment data from ",fname)
  raw <- readChar(fname, file.info(fname)$size)
  raw <- gsub("\r","",raw)
  raw <- unlist(strsplit(raw, "\n"))
  experimentParts<-matrix(, nrow = 0, ncol = 3)
  colnames(experimentParts)<-c("verb","value 1","value 2")
  for (line in raw){
    lineVal1 <- NA
    lineVal2 <- NA
    if (substr(line[1],1,1)=="#") {
      lineKey<-line
    } else {
      line<-unlist(strsplit(line, "="))
      lineKey<-line[1]
      lineVals<-line<-unlist(strsplit(line[2], "-"))
      lineVal1<-lineVals[1]
      lineVal2<-lineVals[2]
    }
    line=c(lineKey,lineVal1,lineVal2)
    experimentParts<-rbind(experimentParts,line)
  } 
  #print(experimentParts)
  return(experimentParts)
}

# create a reference class obect to represent an ROI folder and its analyzed data.
# no information about how to analyze this data belongs here. 
# Just attributes describing the ROI folder.
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

# given an RoiFolder object, plot its delta F/F chart
plot_ROI_DFF<-function(ROI,saveAs="NULL"){
  
  if (saveAs!="NULL") {
    message("preparing to create a PNG file")
    png(filename=saveAs, width=8, height=6, units="in", type="cairo", res=200)
  }
  
  matplot(as.numeric(rownames(ROI$dataDFF))/60, ROI$dataDFF*100, type='l', lw=3, lty=1, 
          xlab = "experiment duration (minutes)",
          ylab = expression(paste(Delta, "  F / F (%)")))
  
  grid()
  abline(h=0,lty="dashed") # draw a horizontal and vertical line
  legend("topleft", colnames(ROI$dataDFF), 
         cex=0.6, # font size
         lty=c(1,1),lw=2, # line style
         col=(1:length(ROI$dataDFF)), # line color
         bty="n" # no background or border
  )
  title(paste("ROI Analysis of",basename(ROI$folder)))
  
  if (saveAs=="NULL") {
    message("not saving figure, so displaying it...")
  } else {
    saveAs=normalizePath(saveAs, mustWork=FALSE)
    message("saving figure: ",saveAs)
    dev.off()
  }
}


################################################################
### PROGRAM STARTS HERE ########################################
################################################################
roi_folder_path<-"X:/Data/SCOTT/2017-05-10 GCaMP6f/GCaMP6f PFC OXTR cre/2017-06-01 cell3"
ROI<-newRoiFolder(roi_folder_path, framePeriod=10, firstRoiBaseline=FALSE)
plot_ROI_DFF(ROI)
plot_ROI_DFF(ROI,saveAs="04.png")