# code here generates figures
#####################################################

# call this inside a plotting function
figureSTART<-function(saveAs){
  if (saveAs!="NULL") {
    saveAs<-normalizePath(saveAs, mustWork=FALSE)
    png(filename=saveAs,width=8, height=6, units="in", type="cairo", res=200)
    message("preparing to save figure as: ",saveAs)
  } else {
    dev.new()
    message("preparing to display figure")
  }
}

# call this inside a plotting function
figureEND<-function(saveAs){
  if (saveAs!="NULL") {
    # turn the driver off because we are done writing the filename
    message("saving figure...")
    dev.off()
    message("saved: ",saveAs)
  } else {
    # don't turn the driver off because we might want to make another one
    message("displaying figure ...")
    dev.next()
  }
}

plot_ROI_RAW<-function(ROI,saveAs="NULL"){
  figureSTART(saveAs)
  matplot(as.numeric(rownames(ROI$dataRaw))/60, ROI$dataRaw*100, type='l', lw=3, lty=1, 
          xlab = "experiment duration (minutes)",
          ylab = "raw pixel value (AFU)")
  title(paste("ROI Analysis of",basename(ROI$folder)))
  grid()
  abline(h=0,lty="dashed") # draw a horizontal and vertical line
  legend("topleft", colnames(ROI$dataRaw), 
         cex=0.6, # font size
         lty=c(1,1),lw=2, # line style
         col=(1:length(ROI$dataRaw)), # line color
         bty="n" # no background or border
  )
  figureEND(saveAs)
}


# given an RoiFolder object, plot its delta F/F chart
plot_ROI_DFF<-function(ROI,saveAs="NULL"){
  figureSTART(saveAs)
  matplot(as.numeric(rownames(ROI$dataDFF))/60, ROI$dataDFF*100, type='l', lw=3, lty=1, 
          xlab = "experiment duration (minutes)",
          ylab = expression(paste(Delta, "  F / F (%)")))
  title(paste("ROI Analysis of",basename(ROI$folder)))
  grid()
  abline(h=0,lty="dashed") # draw a horizontal and vertical line
  legend("topleft", colnames(ROI$dataDFF), 
         cex=0.6, # font size
         lty=c(1,1),lw=2, # line style
         col=(1:length(ROI$dataDFF)), # line color
         bty="n" # no background or border
  )
  figureEND(saveAs)
}