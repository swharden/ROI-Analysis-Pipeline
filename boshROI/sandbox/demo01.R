library(devtools)
library(colorRamps)

load_all("../../boshROI")
results.dt <- roi_read_results("../../data/cell1/Results.xls")
for (i in (1:ncol(results.dt))){ 
    results.dt[,1]<-as.numeric(as.character(results.dt[,i])) - as.numeric(as.character(results.dt[,1]))
}


#print(colnames(results.dt))
Xs <- as.numeric(rownames(results.dt)) # row names are X units (seconds)
Xs <- Xs/60 # now in minutes

# start a plot by choosing the format
png("demo.png", width=8, height=6, units="in", type="cairo", res=300)

# establish coords by plotting invisibly, then grid the plot
plot(Xs, results.dt[,1], type="n", ann=FALSE)
grid()

# plot the actual (visible) data

# start by determining a colormap
#colors <- rainbow(ncol(results.dt)*2)
colors <- colorRamps::magenta2green(ncol(results.dt))
for (i in (1:ncol(results.dt))){
	# add transparency to the color
	color=paste(colors[i],"99",sep = "")
	# plot the line
	lines(Xs, results.dt[,i], col=color, lwd = 2)
}

# add labels
title(main="Raw Pixel Intensity")
title(xlab="Experiment Duration (minutes)")
title(ylab="Pixel Value (AFU)")

# flush the image memory into the output file
invisible(dev.off())