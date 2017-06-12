#install.packages("tiff")
library(tiff)

system("mkdir ./results")

fnames <- Sys.glob("*.ome.tif")
fnames1 <- gsub(".ome.tif", "", fnames, fixed = TRUE)

for(fileN in 1:length(fnames)){
  assign(fnames1[fileN],readTIFF(paste(fnames[fileN]), info = TRUE, as.is = TRUE))
}

rowmeans.names<-matrix(ncol=length(fnames1))
rowmeans.names<-matrix()
rowmeans.names<-dim(NULL)

for (x in fnames1[1:length(fnames1)]){
  #rowmeans.names <- data.frame(1:length(fnames1))
    xdf<- get(x, envir = .GlobalEnv);
    rowmeans <- paste0(x,".rowmeans");
    rowmeans.names[x] <- cbind(assign(rowmeans, as.data.frame(apply(xdf, 1, mean))))
}
rowmeans.df<- as.data.frame(rowmeans.names) 


