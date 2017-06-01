####### INSTALL STUFF #######
##install.packages("readr")
##install.packages("data.table")
##install.packages("reshape2")
##install.packages("ggplot2")

#system("Rscript --vanilla \\Spike\X_Drive\Data\SCOTT\2017-05-10 GCaMP6f\2017-05-10 GCaMP6f PFC OXTR cre\2017-06-01 cell2 Results.xls")

# Rscript --vanilla /GitHub/ROI-Analysis-Pipeline/R/updated.R
#! usr/bin/env Rscript
args <- commandArgs(TRUE)  
setwd(args[1])
wd.name <- basename(getwd())
res.pref = 1000  # set graph resolution (ppi)

####### ROI Analysis ########
sinkfile <- file("messages.Rout", open = "wt")
sink(sinkfile, type = "message")

library(utils)
library(readr)
library(data.table)
library(reshape2)
library(ggplot2)

cat("\nLOADING: ",normalizePath("Results.xls"),"\n")

cell.dt <- read_tsv("Results.xls")
colnames(cell.dt)[1] <- "frame" 
ROImeans.dt <- cell.dt[,2:length(cell.dt), drop=FALSE]   # Keeps only "Mean_" columns (ROI mean values)
actual.frames = cell.dt[,1, drop=FALSE]   # Keeps only "frames" column


fnames <- Sys.glob("*.tif")
fnames1 <- gsub(".tif", "", fnames, fixed = TRUE)
fnames2 <- as.double(fnames1)
t0 <- (fnames2[1])-((fnames2[3])-(fnames2[2]))

fnames2[is.na(fnames2)] <- t0 
fnames3 <- sort(fnames2)
fnames3.df <- as.data.frame(fnames3)
colnames(fnames3.df)[1]<-"time"

subtract.funct <- function(x) {(x-t0)/60}
fnames.df <- as.data.frame(subtract.funct(fnames3.df))
frame.time <- cbind(actual.frames, fnames.df)

if (anyDuplicated(fnames.df)==0) +
  if (is.numeric(fnames.df[1:length(fnames.df),])==TRUE) + 
  if (nrow(fnames.df)==nrow(cell.dt)){
       cell.dt<-cbind(fnames.df[,1, drop=FALSE], cell.dt[,2:length(cell.dt)])} else{
         cat("\nCheck tiff file names. Frame times read from file names in the format \"[time].tif\" (e.g. 149177004.547.tif.) Proceeding with frame number instead of time.\n")}

###
colnames(cell.dt)[1] <- "frame" 
frames = cell.dt[,1, drop=FALSE]   # Keeps only "frames" column

#############################

df.m <- melt(cell.dt, id.vars='frame')   #restructuring the data
colnames(df.m) <- c("frame", "ROI", "Ft")  #renaming columns

#############################
#### Creating functions #####

# dF/Fb = (Ft-Fb)/Fb #

# Fb = mean(Ft_b1:b2) #
# b1 = Ft at frame 2500
# b2 = Ft at frame 3400

Fbnorm.func <- function(Ft, Fb){
  result <- (Ft - Fb)/Fb
  return(result)
}

###

subtract.FbROI.func <- function(dF.Fb, Mean1){
  result1 <- (dF.Fb - Mean1)
  return(result1)
}

#############################

means.mat <- as.matrix(ROImeans.dt)
listofROIs <- as.list(colnames(means.mat))
listofROIs1 <- as.character(listofROIs)
listofROIs2.df <- as.data.frame(listofROIs1)
colnames(listofROIs2.df) <- c("ROI")

#############################
cat("\nLOADING: ",normalizePath("experiment.txt"),"\n")

experiment.info <- read_lines("experiment.txt")
exp.info <- experiment.info[1]

experiment <- read_lines("experiment.txt", skip=1)
exp <- gsub("=", ",", experiment)
exp1 <- gsub("-", ",", exp)
exp.values <- read.table(textConnection(exp1), sep = ",", row.names = 1, col.names = c("condition","b1","b2"))

b.range <- exp.values["baseline",1:2]
TGOT.range <- exp.values["TGOT",1:2]
cond.range.df <- rbind(b.range, TGOT.range)

Fb.range <- cell.dt[(b.range[[1]]:b.range[[2]]), , drop=FALSE]
Fb.values <- Fb.range[ ,2:length(Fb.range), drop=FALSE]
Fb.values.mat <- as.matrix(Fb.values)

Fb.df <- as.data.frame(apply(Fb.values.mat, 2, mean)) #creates a dataframe of mean Fb values for each ROI
colnames(Fb.df) <- c("Fb")   #renaming column
Fb.df1 <- cbind(listofROIs2.df, Fb.df)

df.m1 <- merge(df.m, Fb.df1, by="ROI")   # Adds 'Fb' column to the data

df.m1$result <- Fbnorm.func(df.m1$Ft, df.m1$Fb)   # running Fb-normalization function (results are added as a new column of data labeled "result")
colnames(df.m1)[colnames(df.m1)=="result"] <- "dF.Fb"   #renaming column

#############################

temp1a <- df.m1[ ,1:2, drop = FALSE]
temp1b <- df.m1[ ,5, drop = FALSE]
df.m2 <- cbind(temp1a, temp1b)
df.unmelted <- dcast(data = df.m2, formula = frame~ROI, fun.aggregate = sum, value.var = "dF.Fb")

adj.bROI.values = df.unmelted[,2, drop=FALSE]   # Keeps only "Mean1" column (baseline ROI values)
df.m3 <- cbind(df.m2, adj.bROI.values)

df.m3$result1 <- subtract.FbROI.func(df.m3$dF.Fb, df.m3$Mean1)   #running function (results are added as a new column of data labeled "result1")
colnames(df.m3)[colnames(df.m3)=="result1"] <- "dF.Fb.adj"   #renaming column of adjusted Ft values

#############################

temp2a <- df.m3[ ,1:2, drop = FALSE]
temp2b <- df.m3[ ,5, drop = FALSE]
dF.Fb.values <- cbind(temp2a, temp2b)

results_1 <- dcast(data = dF.Fb.values, formula = frame~ROI, fun.aggregate = sum, value.var = "dF.Fb.adj")

results_2a <- results_1[,1, drop=FALSE]
results_2b <- as.data.frame(apply(results_1[2:length(results_1)], 2, function(x) x*100))
results_B <- cbind(results_2a, results_2b)

write.table(results_B, file = "results_B.xls", row.names = FALSE, sep="\t", quote = FALSE) 
cat("\nSAVED: ",normalizePath("results_B.xls"),"\n")

#############################

mean.dF.F <- as.data.frame(apply(results_B[,3:length(results_B)], 1, mean))

stdev.dF.F <- as.data.frame(apply(results_B[,3:length(results_B)], 1, sd))

stats.dF.F <- cbind(results_B$frame, mean.dF.F, stdev.dF.F)
colnames(stats.dF.F) <- c("frame", "mean.dF.F", "stdev.dF.F")

graph.data <- cbind(results_B, stats.dF.F[,2, drop=FALSE])
graph.data.m <- melt(graph.data, id.vars='frame')   #restructuring the data
colnames(graph.data.m) <- c("frame", "ROI", "dF.F")  #renaming columns

traces.data1 <- cbind(results_B[,1], results_B[,3:length(results_B)])  # excludes Mean1 (baseline ROI)
traces.data <- cbind(stats.dF.F[,1:2, drop=FALSE], traces.data1[,2:length(traces.data1)])
traces.data.m <- melt(traces.data, id.vars='frame')
colnames(traces.data.m) <- c("frame", "ROI", "dF.F")

####

cr.df <- cond.range.df
ft.df <- frame.time

ft.b1 <- ft.df[ft.df$frame==(cr.df[['baseline',1]]),]
ft.b2 <- ft.df[ft.df$frame==(cr.df[['baseline',2]]),]
ft.t1 <- ft.df[ft.df$frame==(cr.df[['TGOT',1]]),]
ft.t2 <- ft.df[ft.df$frame==(cr.df[['TGOT',2]]),]

b.xmin=ft.b1[['time']] 
b.xmax=ft.b2[['time']]
t.xmin=ft.t1[['time']]
t.xmax=ft.t2[['time']]

####### Graphing Data #######

rplot1 <- ggplot(data=traces.data.m, aes(x=traces.data.m[['frame']], y=(traces.data.m[['dF.F']]))) + theme_bw() +
  geom_rect(xmin=b.xmin, xmax=b.xmax, ymin=-Inf, ymax=Inf, fill="seagreen1", alpha=0.002) +
  geom_rect(xmin=t.xmin, xmax=t.xmax, ymin=-Inf, ymax=Inf, fill="yellow", alpha=0.002) + 
  geom_line(aes(colour=ROI, alpha=0.07), show.legend = FALSE) 

rplot1 + labs(y = "dF/F (%)") +
  labs(x = "Experiment Duration (min)") +
  labs(title = expression(paste("GCaMP6f: Ca"^"2+"*" Activity-- ROI Traces")), subtitle = paste(wd.name, exp.info)) +
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(plot.subtitle = element_text(hjust = 0.5)) +
  scale_x_continuous(expand = c(0.006,0)) +
  png(filename = "fig_traces.png", width = 6, height = 4, units = "in", type="cairo", res = res.pref)
dev.off()

cat("\nSAVED: ",normalizePath("fig_traces.png"),"\n")
##

rplot2 <- ggplot(data=stats.dF.F, aes(x=stats.dF.F[['frame']])) +
  geom_rect(xmin=b.xmin, xmax=b.xmax, ymin=-Inf, ymax=Inf, fill="seagreen1", alpha=0.002) +
  geom_rect(xmin=t.xmin, xmax=t.xmax, ymin=-Inf, ymax=Inf, fill="yellow", alpha=0.002) 

rplot2 + geom_ribbon(aes(ymin=stats.dF.F[['mean.dF.F']]-stats.dF.F[['stdev.dF.F']], ymax=stats.dF.F[['mean.dF.F']]+stats.dF.F[['stdev.dF.F']]), fill="grey", alpha=0.3) +
  geom_line(aes(y=(stats.dF.F[['mean.dF.F']]))) + theme_bw() + 
  labs(y = "dF/F (%)") +
  labs(x = "Experiment Duration (min)") +
  labs(title = expression(paste("GCaMP6f: Ca"^"2+"*" Activity-- ROI Average")), subtitle = paste(wd.name, exp.info)) +
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(plot.subtitle = element_text(hjust = 0.5)) +
  scale_x_continuous(expand = c(0.006,0)) +
  png(filename = "fig_av.png", width = 6, height = 4, units = "in", type="cairo", res = res.pref)
dev.off()

cat("\nSAVED: ",normalizePath("fig_av.png"),"\n")
cat("\nDONE! \n")
sink()
