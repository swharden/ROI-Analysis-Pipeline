# ROI analysis #
################
# Reading data from TIF files:

install.packages("RImageJROI")
install.packages("tiff")
install.packages("raster")
install.packages("rgdal")

library(RImageJROI)
library(spatstat)
library(spatstat.utils) 
library(tiff)
library(rgdal)

my.ijzip <- read.ijzip("RoiSet.zip", names=FALSE)


my.ijzip.names <- split(my.ijzip.listfiles, my.ijzip.listfiles$name)
my.ijspatstats <- ij2spatstat(my.ijzip)
myijstats <- my.ijspatstats

plot(my.ijzip)

fnames <- Sys.glob("*.tif")
fnames1 <- gsub(".tif", "", fnames, fixed = TRUE)

# Read each TIF file into matrix: #

for(fileN in 1:length(fnames)){
  assign(fnames1[fileN],readTIFF(paste(fnames[fileN])))
}

for(roi in 1:length(my.ijzip)){
  assign(paste("rect", roi, sep=""),my.ijzip[roi])
}

for(roi in 1:length(myijstats)){
  assign(paste("rect", roi, sep=""),myijstats[roi])
}

ijstat.m <- as.matrix(myijstats)
ijstat.df <- as.data.frame(myijstats)
ij.df2 <- apply(ijstat.df, 2, unique) #dataframe of x and y ranges 










