####### Run 1 #########

#getwd()
#setwd("~/data") # or ctrl+shift+H # Choose a working directory

library(readr)
filename <- "X:\\Data\\SCOTT\\2017-05-10 GCaMP6f\\2017-05-10 GCaMP6f PFC GABA cre\\2017-05-23 cell2.csv"
filename <- gsub("\\\\","/",filename)
cell.dt <- read_csv(filename)
colnames(cell.dt)[colnames(cell.dt)=="X1"] <- "frame"   #renaming column

ROImeans.dt <- cell.dt[,2:length(cell.dt), drop=FALSE]   # Keeps only "Mean_" columns (ROI mean values)

#
# frame 1 = "time 0" --> initial fluorescence = Fi
#Ft = fluorescence at time 't' (each frame is a time interval)
#
# dF/F = (Ft-Fi)/Fi
#
############################

library(reshape2) 

melted.df <- melt(cell.dt, id.vars='frame')   #restructuring the data

colnames(fi.list.melted) <- c("value", "variable")   #renaming the columns (necessary in order to merge in next step)

df.m <- merge(melted.df, fi.list.melted, by="variable")   # Adds 'Fi' column to the data

colnames(df.m) <- c("ROI", "t", "Ft", "Fi")  #renaming columns
head(df.m)

ggplot(data=df.m, aes(x=t, y=Ft, colour=ROI)) +
  geom_point(size=0.01)

##############################
#### Creating a function #####

# dF/F = (Ft-Fi)/Fi #

myfunc <- function(Ft, Fi){
  result <- (Ft - Fi)/Fi
  return(result)
}

#### Running the Function ####

df.m$results <- myfunc(df.m$Ft, df.m$Fi)   #running function (results are added as a new column of data)
colnames(df.m)[colnames(df.m)=="results"] <- "dF/F"   #renaming column


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
cell.mat <- as.matrix(cell.dt)

Fb.range <- cell.dt[2500:3400, , drop=FALSE]
Fb.frames <- Fb.range[ ,1, drop=FALSE]
Fb.values <- Fb.range[ ,2:length(Fb.range), drop=FALSE]

Fb.range.mat <- cell.mat[2500:3200, , drop=FALSE]
Fb.values.mat <- as.matrix(Fb.values)
Fb.df <- as.data.frame(apply(Fb.values.mat, 2, mean))
colnames(Fb.df) <- c("Fb")   #renaming column
Fb.df1 <- cbind(listofROIs2.df, Fb.df)

df.m1 <- merge(df.m, Fb.df1, by="ROI")   # Adds 'Fb' column to the data

# Fb = mean(Ft_b1:b2) #
# b1 = Ft at frame 2500
# b2 = Ft at frame 3400

Fbnorm.func <- function(Ft, Fb){
  result1 <- (Ft - Fb)/Fb
  return(result1)
}

df.m1$result1 <- Fbnorm.func(df.m1$Ft, df.m1$Fb)   #running function (results are added as a new column of data)
colnames(df.m1)[colnames(df.m1)=="result1"] <- "dF/Fb"   #renaming column


#######

r.func <- function(Ft, Fb){
  result2 <- Ft/Fb
  return(result2)
}

df.m1$result2 <- r.func(df.m1$Ft, df.m1$Fb)   #running function (results are added as a new column of data)
colnames(df.m1)[colnames(df.m1)=="result2"] <- "r"   #renaming column

#####################################################

merged.all.df <- merge(df.m1, ROIstats.df, by="ROI")

finaldata <- merged.all.df
head(finaldata)

write.csv(finaldata, file = "2017-05-23_run2_finaldata.csv") 


#### Graphing Data #####

ggplot(data=finaldata, aes(x=t, y=Ft, colour=ROI)) +
  geom_point(size=0.01) +
  tiff(filename = "2017-05-23_run2_Ft_values_graph.tiff",
       width = 1080, height = 530, units = "px")
dev.off()

ggplot(data=finaldata, aes(x=t, y=finaldata[['dF/F']], colour=ROI)) +
  geom_point(size=0.01) +
  tiff(filename = "2017-05-23_run2_dF-F_values_graph.tiff",
       width = 1080, height = 530, units = "px")
dev.off()

ggplot(data=df.m1, aes(x=t, y=df.m1[['dF/Fb']], colour=ROI)) +
  geom_point(size=0.01) +
  tiff(filename = "2017-05-23_run2_dF-Fb_values_graph.tiff",
       width = 1080, height = 530, units = "px")
dev.off()

ggplot(data=df.m1, aes(x=t, y=r, colour=ROI)) +
  geom_point(size=0.01) +
  tiff(filename = "2017-05-23_run2_r_values_graph.tiff",
       width = 1080, height = 530, units = "px")
dev.off()


ggplot(data=df.m1, aes(x=t, y=(r-1)*100, colour=ROI)) +
  geom_point(size=0.01) +
  tiff(filename = "2017-05-23_run2_d_values_graph.tiff",
       width = 1080, height = 530, units = "px")
dev.off()

#####

rplot <- ggplot(data=df.m1, aes(x=t, y=(r-1)*100, colour=ROI)) +
  geom_point(size=0.02) 
rplot + labs(y = "dF/F (%)") +
  labs(x = "Time (frames/ms)") +
  labs(title = expression(paste("GCaMP6f: Ca"^"2+"*" Activity")), subtitle = "Run 2: TTX + TGOT") +
  theme(plot.title = element_text(hjust = 0.5)) +
  #scale_fill_continuous(guide = guide_legend(keywidth = 7, keyheight = 12)) +
  scale_x_continuous(expand = c(0.006,0))
# 2017-05-23 run2 d-plot


################################