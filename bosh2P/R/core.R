#' test
#' @export
test <- function(){
  message("This is a test function.")
}

load_2ptiff <- function(tiff.filename= "*.tif", ignore.source=TRUE, ignore.more = NULL){
  fnames <- Sys.glob(paste0(tiff.filename))
  if (ignore.source = TRUE){
    fnames <- fnames[grep("Source", fnames, ignore.case = TRUE, invert = TRUE)]
  }
  if (ignore.more!="NULL"){
    fnames <- fnames[grep(paste0(ignore.more), fnames, invert = TRUE)]
  }
  fnames1 <- gsub(".tif", "", fnames, fixed = TRUE)
  for(fileN in 1:length(fnames)){
    assign(fnames1[fileN], readTIFF(paste(fnames[fileN]), info = TRUE, as.is = TRUE))
  }
  rowmeans.names<-dim(NULL)
  for (x in fnames1[1:length(fnames1)]){
    #rowmeans.names <- data.frame(1:length(fnames1))
    xdf<- get(x, envir = .GlobalEnv);
    rowmeans <- paste0(x,".rowmeans");
    rowmeans.names[x] <- cbind(assign(rowmeans, as.data.frame(apply(xdf, 1, mean))))
  }
  traces <- as.data.frame(rowmeans.names)
  return(traces.av)
}

trace_norm <- function(traces.av, auto.detect = TRUE){
  GoR.fun <- function(green, red){
    GoR = green/red
    return(GoR)
  }
  if (auto.detect = TRUE){
    if (((apply(traces.av[1],2,mean))<(apply(traces.av[2],2,mean)))==TRUE){
      colnames(traces.av)<-c("green", "red")
    } else {
      if (((apply(traces.av[1],2,mean))>(apply(traces.av[2],2,mean)))==TRUE){
        colnames(traces.av)<-c("red", "green")
      } else {
        message("Caution: mean(channel 1) = mean(channel 2); May want to check data for accuracy.")
      }
    }
  } else {
    if (auto.detect = FALSE){
      colnames(traces.av)<-c("red", "green")
    }
  }
  traces.av$GoR = GoR.fun(traces.av$green, traces.av$red)
  GoR.t0 <- traces.av$GoR[1]
  traces.av$dGoR <- traces.av$GoR - GoR.t0
  return(traces.av)
}

