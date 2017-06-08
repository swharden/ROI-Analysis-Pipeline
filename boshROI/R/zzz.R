# code here runs when the package is loaded
#####################################################

.onLoad <- function(libname, pkgname){

	# determine the path to this script and the base directory
	initial.options <- commandArgs(trailingOnly = FALSE)
	script.name <- sub("--file=", "", initial.options[grep("--file=", initial.options)])
	script.basename <- dirname(script.name)
	script.abspath <- dirname(normalizePath(script.basename))
	#print(initial.options)

	# scan the arguments to see if we are expected to analyze an ROI folder
	if("--analyzeRoiFolder" %in% initial.options){
		# the analysis folder is the next item in the list of arguments
		folder <- initial.options[(which(initial.options == "--analyzeRoiFolder")+1)]
		message("I WAS TOLD TO ANALYZE THIS FOLDER: ",folder)
	}
  
}