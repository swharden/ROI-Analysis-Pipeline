# Notes related to matrix and loading CSV data

framePeriod=10 # seconds

rawData <- as.matrix(read.csv("../../../data/cell1/Results.xls", sep="\t"))
rawData <- rawData[,-1:0] # chop off the first column (frame number)
rawData <- rawData-rawData[,1] # subtract-out the first column
rawData <- rawData[,-1:0] # chop off the first column (now 0)

frameTimes <- (1:nrow(rawData))-1 # just an ascending number series
frameTimes <- frameTimes * framePeriod / 60 # turn it to minutes

png(filename="03.png", width=8, height=6, units="in", type="cairo", res=200)
matplot(frameTimes, rawData, type='l', lw=3, lty=1, 
        xlab = "Experiment Duration (minutes)",
        ylab = expression(paste(Delta, "  Mean Pixel Intensity (AFU)"))
        )
grid()
abline(h=0,lty="dashed") # draw a horizontal and vertical line
legend("topleft", colnames(rawData), 
       cex=0.6, # font size
       lty=c(1,1),lw=2, # line style
       col=(1:length(rawData)), # line color
       bty="n" # no background or border
       )
title("Raw ROI Pixel Values")

dev.off()