# this script is going to be called from the web server.
# arguments will be given to let the script know what to do.
# for now, assume the only argument is the path to an ROI folder.

message("### RSCRIPT EXECUTION STARTED ###")

### read input arguments

# determine the path to this script and the base directory
initial.options <- commandArgs(trailingOnly = FALSE)
script.name <- sub("--file=", "", initial.options[grep("--file=", initial.options)])
script.basename <- dirname(script.name)

# perform relative imports relative to the script directory
source(paste(sep="/", script.basename, "figure.R"))
source(paste(sep="/", script.basename, "data.R"))

# scan the arguments to see if we are expected to analyze an ROI folder
if("--analyzeRoiFolder" %in% initial.options){
    # the analysis folder is the next item in the list of arguments
    folder=initial.options[(which(initial.options == "--analyzeRoiFolder")+1)]
    message("ANALYZING ROI FOLDER:",folder)
}

# display a message to let the user know the scrpit was successful
message("### RSCRIPT EXECUTION COMPLETE ###")