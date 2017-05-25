####### Run 2 #########

#getwd()
#setwd("~/data") # or ctrl+shift+H # Choose a working directory

#install.packages("readr")
library(readr)

filename <- "X:\\Data\\SCOTT\\2017-05-10 GCaMP6f\\2017-05-10 GCaMP6f PFC GABA cre\\2017-05-23 cell2.csv"
filename <- gsub("\\\\","/",filename)
cell.dt <- read_csv(filename)
colnames(cell.dt)[colnames(cell.dt)=="X1"] <- "frame"   #renaming column

ROImeans.dt <- cell.dt[,2:length(cell.dt), drop=FALSE]   # Keeps only "Mean_" columns (ROI mean values)

#################################

#install.packages("reshape2")
library(reshape2)

df.m <- melt(cell.dt, id.vars='frame')   #restructuring the data

colnames(df.m) <- c("t", "ROI", "Ft")  #renaming columns
head(df.m)


# Plot data to choose b values: #

#install.packages("ggplot2")
library(ggplot2)

ggplot(data=df.m, aes(x=t, y=Ft, colour=ROI)) +
  geom_point(size=0.01)

##############################
#### Creating a function #####

# dF/Fb = (Ft-Fb)/Fb #

# Fb = mean(Ft_b1:b2) #
# b1 = Ft at frame 2500
# b2 = Ft at frame 3400

Fbnorm.func <- function(Ft, Fb){
  result1 <- (Ft - Fb)/Fb
  return(result1)
}

##############################

means.mat <- as.matrix(ROImeans.dt)
mean.of.ROImeans.df <- as.data.frame(apply(means.mat, 2, mean))
colnames(mean.of.ROImeans.df) <- c("mean(Ft)")

listofROIs <- as.list(colnames(means.mat))
listofROIs1 <- as.character(listofROIs)
listofROIs2.df <- as.data.frame(listofROIs1)
colnames(listofROIs2.df) <- c("ROI")

stdev.of.ROImeans.df <- as.data.frame(apply(means.mat, 2, sd))
colnames(stdev.of.ROImeans.df) <- c("stdev(Ft)")

ROIstats.df <- cbind(listofROIs2.df, mean.of.ROImeans.df, stdev.of.ROImeans.df)

###############################

Fb.range <- cell.dt[2500:3400, , drop=FALSE]
#Fb.frames <- Fb.range[ ,1, drop=FALSE]
Fb.values <- Fb.range[ ,2:length(Fb.range), drop=FALSE]
Fb.values.mat <- as.matrix(Fb.values)

Fb.df <- as.data.frame(apply(Fb.values.mat, 2, mean)) #creates a dataframe of mean Fb values for each ROI
colnames(Fb.df) <- c("Fb")   #renaming column
Fb.df1 <- cbind(listofROIs2.df, Fb.df)

df.m1 <- merge(df.m, Fb.df1, by="ROI")   # Adds 'Fb' column to the data


df.m1$result1 <- Fbnorm.func(df.m1$Ft, df.m1$Fb)   #running function (results are added as a new column of data labeled "result1")
colnames(df.m1)[colnames(df.m1)=="result1"] <- "dF/Fb"   #renaming column

#####################################################

finaldata <- merge(df.m1, ROIstats.df, by="ROI")
head(finaldata)

write.csv(finaldata, file = "2017-05-23_run2_finaldata.csv") 

##### Graphing Data ######

# Graph of ROI Ft values #
ggplot(data=finaldata, aes(x=t, y=Ft, colour=ROI)) +
  geom_point(size=0.01) 

# Graph of ROI dF/Fb values #
ggplot(data=finaldata, aes(x=t, y=finaldata[['dF/Fb']], colour=ROI)) +
  geom_point(size=0.01) 

# Graph of ROI dF/Fb percentages #
ggplot(data=finaldata, aes(x=t, y=(finaldata[['dF/Fb']])*100, colour=ROI)) +
  geom_point(size=0.01) 

#####

rplot <- ggplot(data=finaldata, aes(x=t, y=(finaldata[['dF/Fb']])*100, colour=ROI)) +
  geom_point(size=0.02) 
rplot + labs(y = "dF/F (%)") +
  labs(x = "Time (frames/ms)") +
  labs(title = expression(paste("GCaMP6f: Ca"^"2+"*" Activity")), subtitle = "Run 2: TTX + TGOT") +
  theme(plot.title = element_text(hjust = 0.5)) +
  #scale_fill_continuous(guide = guide_legend(keywidth = 7, keyheight = 12)) +
  scale_x_continuous(expand = c(0.006,0))
# 2017-05-23 run2 d-plot

################################