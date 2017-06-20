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
#library(rgdal)

my.ijzip <- read.ijzip("RoiSet.zip", names=FALSE)

my.ijspatstats <- ij2spatstat(my.ijzip)
plot(my.ijzip)

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
for(fileN in 1:length(fnames)){
  assign(fnames[fileN],readTIFF(paste(fnames[fileN]), info = TRUE, as.is = TRUE))
}

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


# for(i in 1:length(xranges)){
#   assign(paste0("xrange",i), eval(parse(text=paste(xranges[i]))))
# }

# for(a in 1:length(xranges)){
#   assign(paste0("df",a), as.data.frame(eval(parse(text=paste(xranges[a])))))
# }

###########
dim.fun <- function(x){
     as.numeric(paste0(x))
}

eval.fun <- function(x){
  result <- eval(parse(text=paste(x)))
  return(result)
}

xfun <- function(x){
  result <- as.data.frame(eval(parse(text=paste(x))))
  return(result)
}

x.df <- as.data.frame(lapply(xranges, xfun))
row.names(x.df) <- c("x1","x2")

y.df <- as.data.frame(lapply(yranges, xfun))
row.names(y.df) <- c("y1","y2")

ranges.df <- rbind(x.df,y.df)
colnames(ranges.df)<- c(paste0("r",1:length(ranges.df)))
ranges.m <- as.matrix(ranges.df)

############
vars <- ranges.df
for (a in 1:length(ranges.m)){
  x1 <- paste0("x1.",a);
    assign(x1, ranges.m['x1',a]);
    vars['x1',a] <- x1;

  x2 <-paste0("x2.",a);
    assign(x2, ranges.m['x2',a]);
    vars['x2',a] <- x2;

  y1 <-paste0("y1.",a);
    assign(y1, ranges.m['y1',a]);
    vars['y1',a] <- y1;

  y2 <-paste0("y2.",a);
    assign(y2, ranges.m['y2',a]);
    vars['y2',a] <- y2
}

fnames.df <- as.data.frame(fnames1)
fnames.df$cell <- fnames.df
colnames(fnames.df)<- c("fnames","cell")

data.df <- data.frame()
for (x in fnames1[1:length(fnames1)]){
  for (n in 1:ncol(ranges.df)){
    cell <- paste0(x,"r",n);
    cellmeans <- paste0(x,".r",n,".means");
    xdf<- get(x, envir = .GlobalEnv)
    y1<-eval.fun(paste0('y1.',n));
    y2<-eval.fun(paste0('y2.',n));
    x1<-eval.fun(paste0('x1.',n));
    x2<-eval.fun(paste0('x2.',n));

      #assign(cell, xdf[dim.fun(y1):dim.fun(y2),dim.fun(x1):dim.fun(x2)]);
      data.df[x,n]<- assign(cellmeans, mean(xdf[dim.fun(y1):dim.fun(y2),dim.fun(x1):dim.fun(x2)]))
  };
}

mean.names <- c(paste0("Mean",1:length(ranges.df)))
colnames(data.df)<-mean.names
write.table(data.df, "demo_imagedata.R.xls", sep="\t", row.names = TRUE, col.names = NA) # Saves a file equivalent to the default output file "Results.xls" given by ImageJ
 ## This file can be used in place of "Results.xls" in boshROI pipeline.

###########
