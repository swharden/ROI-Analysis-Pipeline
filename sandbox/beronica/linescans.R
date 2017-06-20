# install.packages("tiff")
# install.packages("readr")
# install.packages("XML")
# install.packages("xml2")
# install.packages("ggplot2")

# Rscript --vanilla /GitHub/ROI-Analysis-Pipeline/R/updated.R

#! usr/bin/env Rscript
args <- commandArgs(TRUE)
setwd(args[1])
wd.name <- basename(getwd())

sinkfile <- file("messages.Rout", open = "wt")
sink(sinkfile, type = "message")

library(tiff)
library(readr)
library(XML)
library(xml2)
library(ggplot2)

xml.name <- Sys.glob("*.xml")
#ls.info <- read_lines(paste(xml.name))
#xml.data <- xmlParse(paste(xml.name))
xml.data2 <- read_xml(paste(xml.name))
xml.nodes <- as_list(xml.data2)
#xml.tree <- xmlTreeParse(paste(xml.name))
#xml.itree <- xmlTreeParse(paste(xml.name), useInternalNodes = TRUE)
#nodeset <-getNodeSet(doc=xml.itree, "xml.itree//PVStateValue//key")
node.xpaths <- xml_path(xml_find_all(xml.data2, ".//PVStateValue"))

# Channel 1 = red, channel 2 = green

dir.create("./results", showWarnings = FALSE)
fnames <- Sys.glob("*.tif")
fnames2 <- fnames[grep("Source", fnames, ignore.case = TRUE, invert = TRUE)]

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
  colnames(rowmeans.df)<-c("green", "red")
} else {
  if (((apply(rowmeans.df[1],2,mean))>(apply(rowmeans.df[2],2,mean)))==TRUE){
    colnames(rowmeans.df)<-c("red", "green")
  } else {
    message("Caution: mean(channel 1) = mean(channel 2); May want to check data for accuracy.")
  }
}

rowmeans.df$GoR = GoR.fun(rowmeans.df$green, rowmeans.df$red)
GoR.t0 <- rowmeans.df$GoR[1]
rowmeans.df$dGoR <- rowmeans.df$GoR - GoR.t0

dGoR.values <- rowmeans.df$dGoR
frames <- rownames(rowmeans.df)
dGoR.df <- as.data.frame(cbind(frames,dGoR.values))

#### red: #
#dev.new()
plotr <- ggplot(data=rowmeans.df, aes(x=as.numeric(rownames(rowmeans.df)))) + theme_bw()
#geom_rect(xmin=b.xmin, xmax=b.xmax, ymin=-Inf, ymax=Inf, fill="seagreen1", alpha=0.002) +
plotr + geom_line(aes(y=rowmeans.df$red), col="magenta") +
  labs(y = "Pixel Intensity") +
  labs(x = "Frame") +
  labs(title = expression(paste("Two-photon Linescans: Red")), subtitle = paste(wd.name)) +
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(plot.subtitle = element_text(hjust = 0.5)) +
  scale_x_continuous(expand = c(0.006,0)) +
  png(filename = "./results/fig_red.png")
dev.off()
cat("\nSAVED: ",normalizePath("./results/fig_red.png"),"\n")

#### green: #
plotg <- ggplot(data=rowmeans.df, aes(x=as.numeric(rownames(rowmeans.df)))) + theme_bw()
#geom_rect(xmin=b.xmin, xmax=b.xmax, ymin=-Inf, ymax=Inf, fill="seagreen1", alpha=0.002) +
plotg + geom_line(aes(y=(rowmeans.df$green)), col="green") +
  labs(y = "Pixel Intensity") +
  labs(x = "Frame") +
  labs(title = expression(paste("Two-photon Linescans: Green")), subtitle = paste(wd.name)) +
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(plot.subtitle = element_text(hjust = 0.5)) +
  scale_x_continuous(expand = c(0.006,0)) +
  png(filename = "./results/fig_green.png")
dev.off()
cat("\nSAVED: ",normalizePath("./results/fig_green.png"),"\n")


#### dG/R: #
plot1 <- ggplot(data=rowmeans.df, aes(x=as.numeric(rownames(rowmeans.df)))) + theme_bw()
  #geom_rect(xmin=b.xmin, xmax=b.xmax, ymin=-Inf, ymax=Inf, fill="seagreen1", alpha=0.002) +
  plot1 + geom_line(aes(y=(rowmeans.df[['dGoR']]))) +
    labs(y = "Pixel Intensity") +
    labs(x = "Frame") +
    labs(title = expression(paste("Two-photon Linescans: dG/R")), subtitle = paste(wd.name)) +
    theme(plot.title = element_text(hjust = 0.5)) +
    theme(plot.subtitle = element_text(hjust = 0.5)) +
    scale_x_continuous(expand = c(0.006,0)) +
    png(filename = "./results/fig_dGoR.png")
  dev.off()
  cat("\nSAVED: ",normalizePath("./results/fig_dGoR.png"),"\n")

#### G/R: #
    plot2 <- ggplot(data=rowmeans.df, aes(x=as.numeric(rownames(rowmeans.df)))) + theme_bw()
    #geom_rect(xmin=b.xmin, xmax=b.xmax, ymin=-Inf, ymax=Inf, fill="seagreen1", alpha=0.002) +
    plot2 + geom_line(aes(y=(rowmeans.df[['GoR']]))) +
      labs(y = "Pixel Intensity") +
      labs(x = "Frame") +
      labs(title = expression(paste("Two-photon Linescans: Green/Red (G/R)")), subtitle = paste(wd.name)) +
      theme(plot.title = element_text(hjust = 0.5)) +
      theme(plot.subtitle = element_text(hjust = 0.5)) +
      scale_x_continuous(expand = c(0.006,0)) +
      png(filename = "./results/fig_GoR.png")
    dev.off()
    cat("\nSAVED: ",normalizePath("./results/fig_GoR.png"),"\n")

cat("\nDONE! \n")
sink()




