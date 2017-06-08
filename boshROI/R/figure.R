# code here generates figures
#####################################################


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