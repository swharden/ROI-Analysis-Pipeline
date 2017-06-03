# this script is going to be called from the web server.
# arguments will be given to let the script know what to do.
# for now, assume the only argument is the path to an ROI folder.

# perform relative imports relative to the script directory
source("figure.R")

# read arguments and make sure the path exists

# ensure we see all needed files:
# Results.xls, experiment.txt, and RoiSet.zip
# if not, warn the user and abort the script early
code<-"goes here"

# make figures one by one
code<-"goes here"

# display a message to let the user know the scrpit was successful
message("### RSCRIPT EXECUTION COMPLETE ###")