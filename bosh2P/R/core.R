#' test
#' @export
test <- function(){
  message("This is a test function.")
}

#' load_2ptiff
#'
#' Reads raw pixel intensity values from TIFF files generated from two-photon linescans.
#' Converts two-dimensional measures of fluorescence intensity into one-dimensional intensity averages.
#' Returns a data frame with average traces across time for each fluorophore.
#'
#' @param tiff Specify a name pattern to search (via Sys.glob) for TIFF files of interest within the same directory.
#' @param ignore.source logical. If TRUE, ignores TIFF files with "source" in the file name.
#' @param ignore.more A character string to ignore additional TIFF files with the given pattern in the file name.
#'
#' @return a data frame containing average trace values for each fluorophore
#'
#' @export


load_2ptiff <- function(tiff= "*.tif", ignore.source=TRUE, ignore.more=NULL){
  fnames <- Sys.glob(paste0(tiff))
  if (ignore.source==TRUE){
    fnames <- fnames[grep("Source", fnames, ignore.case = TRUE, invert = TRUE)]
  } else {
    fnames = fnames
  }
  if (is.null(ignore.more)==FALSE){
    fnames <- fnames[grep(paste0(ignore.more), fnames, invert = TRUE)]
  } else {
    fnames = fnames
  }
  fnames1 <- gsub(".tif", "", fnames, fixed = TRUE)
  for(fileN in 1:length(fnames)){
    assign(fnames1[fileN], tiff::readTIFF(paste(fnames[fileN]), info = TRUE, as.is = TRUE))
  }
  rowmeans.names<-dim(NULL)
  for (x in fnames1[1:length(fnames1)]){
    #rowmeans.names <- data.frame(1:length(fnames1))
    xdf<- get(x);
    rowmeans <- paste0(x,".rowmeans");
    rowmeans.names[x] <- cbind(assign(rowmeans, as.data.frame(apply(xdf, 1, mean))))
  }
  traces <- as.data.frame(rowmeans.names)
  return(traces)
}

# traces<-load_2ptiff()

#' trace_norm
#'
#' Reads a data frame of averaged (one-dimensional) pixel intensity values for two fluorophore channels (one as a baseline)
#' and calculates normalized fluorescence intensity over time.
#' Returns a data frame with average intensity across time for each fluorophore, average intesity divided by the baseline (G/R), and normalized intensity (dG/R).
#'
#' @param traces a data frame containing average trace values for each fluorophore.
#' @param auto.detect logical. If TRUE, selects the fluorophore channel with the higher mean intensity as the baseline.
#' @param baseline_fluor A character string to indicate the name of the baseline fluorophore.
#' @param indicator_fluor A character string to indicate the name of the indicator fluorophore.
#'
#' @return a data frame containing average trace values for each fluorophore and normalized intensity values.
#'
#' @export
trace_norm <- function(traces, auto.detect = TRUE, baseline_fluor="red", indicator_fluor="green"){
  GoR.fun <- function(green, red){
    GoR = green/red
    return(GoR)
  }
  if (auto.detect==TRUE){
    traces.m <- as.matrix(traces)
    if (((mean(traces.m[,1]))<(mean(traces.m[,2])))==TRUE){
      colnames(traces)<-c("green", "red")
    } else {
      if (((mean(traces.m[,1]))>(mean(traces.m[,2])))==TRUE){
        colnames(traces)<-c("red", "green")
      } else {
        message("Caution: mean(channel 1) = mean(channel 2); May want to check data for accuracy.")
      }
    }
  } else {
    if (auto.detect==FALSE){
      colnames(traces)<-c("red", "green")
    }
  }
  traces$GoR = GoR.fun(traces$red, traces$green)
  GoR.t0 <- traces$GoR[1]
  traces$dGoR <- traces$GoR - GoR.t0
  names(traces)[dimnames(traces)[[2]]=="red"]<- paste0(baseline_fluor)
  names(traces)[dimnames(traces)[[2]]=="green"]<-paste0(indicator_fluor)
  return(traces)
}
# norm <- trace_norm(traces)
