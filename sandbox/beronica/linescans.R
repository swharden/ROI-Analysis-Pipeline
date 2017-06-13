#install.packages("tiff")
library(tiff)
library(readr)
library(XML)
library(xml2)

xml.name <- Sys.glob("*.xml")
#ls.info <- read_lines(paste(xml.name))
#xml.data <- xmlParse(paste(xml.name))
xml.data2 <- read_xml(paste(xml.name))
xml.nodes <- as_list(xml.data2)
#xml.tree <- xmlTreeParse(paste(xml.name))
#xml.itree <- xmlTreeParse(paste(xml.name), useInternalNodes = TRUE)
#nodeset <-getNodeSet(doc=xml.itree, "xml.itree//PVStateValue//key")
node.xpaths <- xml_path(xml_find_all(xml.data2, ".//PVStateValue"))

try(system("mkdir ./results"), silent = TRUE)
fnames <- Sys.glob("*.ome.tif")
if (length(fnames)==0){
  fnames <- Sys.glob("*.tif");
  fnames1 <- gsub(".tif", "", fnames, fixed = TRUE)
} else{
  fnames1 <- gsub(".ome.tif", "", fnames, fixed = TRUE)
}


for(fileN in 1:length(fnames)){
  assign(fnames1[fileN],readTIFF(paste(fnames[fileN]), info = TRUE, as.is = TRUE))
}

rowmeans.names<-dim(NULL)
for (x in fnames1[1:length(fnames1)]){
  #rowmeans.names <- data.frame(1:length(fnames1))
    xdf<- get(x, envir = .GlobalEnv);
    rowmeans <- paste0(x,".rowmeans");
    rowmeans.names[x] <- cbind(assign(rowmeans, as.data.frame(apply(xdf, 1, mean))))
}
rowmeans.df<- as.data.frame(rowmeans.names) 

# delta(green/red) calculation #
## Green/Red: 
GoR.fun <- function(green, red){
  GoR = green/red 
  return(GoR)
}

if (((apply(rowmeans.df[1],2,mean))<(apply(rowmeans.df[2],2,mean)))==TRUE){
  colnames(rowmeans.df[1])<-"green";
  colnames(rowmeans.df[2])<-"red"
} else {
  if (((apply(rowmeans.df[1],2,mean))>(apply(rowmeans.df[2],2,mean)))==TRUE){
    colnames(rowmeans.df[2])<-"green";
    colnames(rowmeans.df[1])<-"red"
  } else {
    print("Caution: mean(channel 1) = mean(channel 2); May want to check data for accuracy.")
  }
}

rowmeans.df$GoR = GoR.fun(rowmeans.df$green, rowmeans.df$red)














