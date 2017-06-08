# code here loads data from (text and images)
#####################################################

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