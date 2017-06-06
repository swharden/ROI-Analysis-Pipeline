# ROI analysis #
################
# Reading data from TIF files:

# install.packages("RImageJROI")
# install.packages("tiff")
# install.packages("raster")
# install.packages("rgdal")

library(RImageJROI)
library(spatstat)
library(spatstat.utils) 
library(tiff)
library(rgdal)

my.ijzip <- read.ijzip("RoiSet.zip", names=FALSE)

my.ijspatstats <- ij2spatstat(my.ijzip)
plot(my.ijzip, legend=names(my.ijzip))

myijstats <- my.ijspatstats
ijstat.names <- names(myijstats)
fullnames <- paste0("myijstats$",ijstat.names)
range.names <- c("xrange", "yrange")
#ijstat.split <- split(myijstats, ijstat.names)
#ijs.mat <- as.matrix(ijstat.split)

xranges <- paste0(fullnames, "[['xrange']]")
yranges <- paste0(fullnames, "[['yrange']]")

fnames <- Sys.glob("*.tif")
fnames1 <- gsub(".tif", "", fnames, fixed = TRUE)


# Read each TIF file into matrix: #

for(fileN in 1:length(fnames)){
  assign(fnames1[fileN],readTIFF(paste(fnames[fileN]), info = TRUE, as.is = TRUE))
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


for(i in 1:length(xranges)){
  assign(paste0("xrange",i), eval(parse(text=paste(xranges[i]))))
}

for(i in 1:length(xranges)){
  assign(paste0("df",i), as.data.frame(eval(parse(text=paste(xranges[i])))))
}

###########
xfun <- function(x){
  result <- as.data.frame(eval(parse(text=paste(x))))
  return(result)
}

x.df <- as.data.frame(lapply(xranges, xfun))
row.names(x.df) <- c("x1","x2")

y.df <- as.data.frame(lapply(yranges, xfun))
row.names(y.df) <- c("y1","y2")

ranges.df <- rbind(x.df,y.df)
colnames(ranges.df)<- c(paste(1:length(ranges.df)))
ranges.m <- as.matrix(ranges.df)
###########

x1.1 <- ranges.m[1]
x2.1 <- ranges.m[2]
y1.1 <- ranges.m[3]
y2.1 <- ranges.m[4]

xy.c1 <- captures0000[as.numeric(paste0(y1.1)):as.numeric(paste0(y2.1)), as.numeric(paste0(x1.1)):as.numeric(paste0(x2.1))]

mean1 <- mean(xy.c1)
############

for (i in 1:length(ranges.m[1:i])){
  assign(paste0("x1.",i), ranges.m['x1',i]);
  assign(paste0("x2.",i), ranges.m['x2',i]);
  assign(paste0("y1.",i), ranges.m['y1',i]);
  assign(paste0("y2.",i), ranges.m['y2',i]);
  range.vars <- c(paste0("x1.",i), paste0("x2.",i), paste0("y1.",i), paste0("y2.",i))
}







