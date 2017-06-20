## setwd("~/Documents/GitHub/ROI-Analysis-Pipeline/bosh2P") #


#' load_2ptiff
#'
#' Reads raw pixel intensity values from TIFF files generated from two-photon linescans.
#' Converts two-dimensional measures of fluorescence intensity into one-dimensional intensity averages.
#' Returns a data frame with average traces across time for each fluorophore.
#'
#' @param tiffNames Specify a name pattern to search (via Sys.glob) for TIFF files of interest within the same directory.
#' @param ignore.source logical. If TRUE, ignores TIFF files with "source" in the file name.
#' @param ignore.more optional. A character string to ignore additional TIFF files with the given pattern in the file name.
#'
#' @return a data frame containing  average raw pixel intensity values for each fluorophore
#'
#' @family LineScan functions
#'
#' @export

load_2ptiff <- function(tiffNames="*.tif", ignore.source=TRUE, ignore.more=NULL){
  fnames <- Sys.glob(paste0(tiffNames))
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
  trace.means<-dim(NULL)
  for (x in fnames1[1:length(fnames1)]){
    #rowmeans.names <- data.frame(1:length(fnames1))
    xdf<- get(x);
    rowmeans <- paste0(x,".rowmeans");
    trace.means[x] <- cbind(assign(rowmeans, as.data.frame(apply(xdf, 1, mean))))
  }
  channelMeans <- as.data.frame(trace.means)
  return(channelMeans)
}

# traces<-load_2ptiff()

#' norm_traces_LS
#'
#' Reads a data frame of averaged (one-dimensional) pixel intensity values for two fluorophore channels (one as a baseline) from a linescan dataset and calculates normalized fluorescence intensity over time.
#' Returns a data frame with average intensity across time for each fluorophore, average intesity divided by the baseline (G/R), and normalized intensity (dG/R).
#'
#' @param channelMeans a data frame containing average trace values for each fluorophore.
#' @param auto.detect logical. If TRUE, selects the fluorophore channel with the higher mean intensity as the baseline.
#' @param channel1.baseline logical. TRUE indicates that channel 1 contains the baseline fluorophore (default red).
#' @param baseline_fluor A character string to indicate the name of the baseline fluorophore.
#' @param indicator_fluor A character string to indicate the name of the indicator fluorophore.
#'
#' @return a data frame containing raw pixel intensity values for each fluorophore over time.
#'
#' @family LineScan functions
#'
#' @export
norm_traces_LS <- function(channelMeans, auto.detect = TRUE, channel1.baseline = TRUE, baseline_fluor = "Red", indicator_fluor = "Green"){
  GoR.fun <- function(green, red){
    GoR = green/red
    return(GoR)
  }
  traces <- channelMeans
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
    if (auto.detect==FALSE && channel1.baseline==TRUE){
      colnames(traces)<-c("red", "green")
    } else{
      if (auto.detect==FALSE && channel1.baseline==FALSE){
        colnames(traces)<-c("green", "red")
      }
    }
  }
  traces$GoR = GoR.fun(traces$red, traces$green)
  GoR.t0 <- traces$GoR[1]
  traces$dGoR <- traces$GoR - GoR.t0
  names(traces)[dimnames(traces)[[2]]=="red"]<- paste0(baseline_fluor)
  names(traces)[dimnames(traces)[[2]]=="green"]<-paste0(indicator_fluor)
  return(traces)
}
# norm <- norm_traces_LS(traces)


## Plotting

#' save_plot_2P
#'
#' @export
save_plot_2P = function(filetype = "png", filename = NULL, width = 6, height = 4, units = "in", type="cairo", res=300){
  if (is.null(filename)){
    filename= basename(getwd())
  }
  eval(call(filetype, filename=filename, width=width, height=height, units=units, type=type, res=res))
}


#### red: #

#' plot_2P_baseline
#'
#' @return a plot of the baseline fluorophore average raw pixel intensity values over time.
#'
#' @family LineScan functions
#'
#' @export
plot_2P_baseline<-function(traces, baseline_fluor="Red", indicator_fluor="Green", ...){
  filename= basename(getwd())
  require(ggplot2)
  names(traces)[dimnames(traces)[[2]]==(paste0(baseline_fluor))]<-"red"
  names(traces)[dimnames(traces)[[2]]==paste0(indicator_fluor)]<-"green"
  plotr <- ggplot2::ggplot(data=traces, aes(x=as.numeric(rownames(traces)))) + theme_bw()
  plotr + geom_line(aes(y=traces$red), col="magenta") +
    labs(y = "Pixel Intensity") +
    labs(x = "Frame") +
    labs(title = paste("Two-photon Linescans:", baseline_fluor), subtitle = paste(filename)) +
    theme(plot.title = element_text(hjust = 0.5)) +
    theme(plot.subtitle = element_text(hjust = 0.5)) +
    #scale_x_continuous(expand = c(0.006,0)) +
    save_plot_2P()
}
# traces <- norm
# plot_2P_baseline(traces)

#### green: #
#' plot_2P_Ca
#'
#' @return a plot of the calcium-sensitive fluorophore average raw pixel intensity values over time.
#'
#' @family LineScan functions
#'
#' @export
plot_2P_Ca<-function(traces, baseline_fluor="Red", indicator_fluor="Green", ...){
  filename= basename(getwd())
  require(ggplot2)
  names(traces)[dimnames(traces)[[2]]==paste0(baseline_fluor)]<-"red"
  names(traces)[dimnames(traces)[[2]]==paste0(indicator_fluor)]<-"green"
  plotr <- ggplot(data=traces, aes(x=as.numeric(rownames(traces)))) + theme_bw()
  #geom_rect(xmin=b.xmin, xmax=b.xmax, ymin=-Inf, ymax=Inf, fill="seagreen1", alpha=0.002) +
  plotr + geom_line(aes(y=traces$green), col="green") +
    labs(y = "Pixel Intensity") +
    labs(x = "Frame") +
    labs(title = paste("Two-photon Linescans:", indicator_fluor), subtitle = paste(filename)) +
    theme(plot.title = element_text(hjust = 0.5)) +
    theme(plot.subtitle = element_text(hjust = 0.5)) +
    scale_x_continuous(expand = c(0.006,0))
}

# plot_2P_Ca(traces)

# #### dG/R: #
#' plot_2P_dGR
#'
#' @return a plot of the delta(G/R) normalized calcium-sensitive fluorophore average pixel intensity values over time.
#'
#' @family LineScan functions
#'
#' @export
plot_2P_dGR <- function(traces, baseline_fluor="Red", indicator_fluor="Green", ...){
  filename= basename(getwd())

  plot1 <- ggplot2::ggplot(data=traces, aes(x=as.numeric(rownames(traces)))) + theme_bw()
  #geom_rect(xmin=b.xmin, xmax=b.xmax, ymin=-Inf, ymax=Inf, fill="seagreen1", alpha=0.002) +
  plot1 + geom_line(aes(y=(traces[['dGoR']]))) +
    labs(y = "Pixel Intensity") +
    labs(x = "Frame") +
    labs(title = expression(paste("Two-photon Linescans: dG/R")), subtitle = paste(filename)) +
    theme(plot.title = element_text(hjust = 0.5)) +
    theme(plot.subtitle = element_text(hjust = 0.5)) +
    scale_x_continuous(expand = c(0.006,0)) +
    save_plot_2P()
}

# #### G/R: #
#' plot_2P_norm
#'
#' @return a plot of the G/R normalized calcium-sensitive fluorophore average pixel intensity values over time.
#'
#' @family LineScan functions
#'
#' @export
plot_2P_norm <- function(traces, baseline_fluor="Red", indicator_fluor="Green", ...){
  filename= basename(getwd())

  plot1 <- ggplot2::ggplot(data=traces, aes(x=as.numeric(rownames(traces)))) + theme_bw()
    #geom_rect(xmin=b.xmin, xmax=b.xmax, ymin=-Inf, ymax=Inf, fill="seagreen1", alpha=0.002) +
  plot1 + geom_line(aes(y=(traces[['GoR']]))) +
    labs(y = "Pixel Intensity") +
    labs(x = "Frame") +
    labs(title = expression(paste("Two-photon Linescans: G/R")), subtitle = paste(filename)) +
    theme(plot.title = element_text(hjust = 0.5)) +
    theme(plot.subtitle = element_text(hjust = 0.5)) +
    scale_x_continuous(expand = c(0.006,0)) +
    do.call(save_plot_2P, ...)
  }


