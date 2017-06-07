library(devtools)
library(colorRamps)
library(reshape2)

load_all("../../boshROI")
results.dt <- roi_read_results("../../data/cell1/Results.xls")
#results.dt[,i]<-as.numeric(as.character(results.dt[,i])) - as.numeric(as.character(results.dt[,1]))


#print(colnames(results.dt))
Xs <- as.numeric(rownames(results.dt)) # row names are X units (seconds)
Xs <- Xs/60 # now in minutes

# start a plot by choosing the format
png("demo.png", width=8, height=6, units="in", type="cairo", res=300)

# establish coords by plotting invisibly, then grid the plot
data <- results.dt
data <- t(data) # rotate
data <- melt(results.dt, id.vars = colnames(results.dt)[0])

plot(data)
#grid()
#title(main="Raw Pixel Intensity")
#title(xlab="Experiment Duration (minutes)")
#title(ylab="Pixel Value (AFU)")

# flush the image memory into the output file
invisible(dev.off())