# code here relates to analyzing ROIs from folders
#####################################################

#' Load data from an ImageJ Results.xls
#'
#' In ImageJ the results of a multi-measure action are
#' usually saved as "Results.xls" (actually a TSV file).
#' This function parses that file and returns a table.
#' 
#' @param results_file path to results TSV file.
#' @param timePeriod time between captures. Leave =1 to frame number
#' @return data table of results
#' @export
#' @examples
#' roi_folder_process("/path/to/ROI/folder/Results.xls")
roi_read_results <- function(results_file, timePeriod=1){
	results_file<-normalizePath(results_file)
	message(" -- loading ",basename(results_file)," ...")
	
	# load our original results and don't modify the data table
	results.dt<-read.table(file=results_file, sep='\t')

	# separate-out pixel data from column names and time points
	data_pixel.dt <- results.dt[2:dim(results.dt)[1],2:dim(results.dt)[2]]
	
	# create new time points as multiples of the timePeriod (and make them row names)
	timePoints <- (1:dim(data_pixel.dt)[1])*timePeriod
	rownames(data_pixel.dt) <- timePoints
	
	# make column names those from the original results file
	colnames(data_pixel.dt) <- as.matrix(results.dt[1,][2:ncol(results.dt)])[1,]
	
	# nwo we have a clean data table of pixel values ONLY with named rows and columns.
	return(data_pixel.dt)
}

#' Ensure an ROI analysis folder has the needed files.
#'
#' This function looks for RoiSet.zip, experiment.txt, and
#' Results.xls. If one of these is missing, the program ends.
#' 
#' @param folder path to ROI folder
#' @export
#' @examples
#' roi_folder_check_files("/path/to/ROI/folder/")
roi_folder_check_files <- function(folder){
	required_files <- c("","RoiSet.zip","experiment.txt")
	for (file_name in required_files){
		file_path <- file.path(folder, file_name)
		file_path <- normalizePath(file_path)
		if (!file.exists(file_path)) {
			stop(gettextf("ERROR: %s does not exist",file_path))
		} else {
			message("  - found ",file_path)
		}
	}
}

#' Automatically process a time series ROI folder.
#'
#' This will create extra dF/F XLS documents, generate
#' figures, etc. The folder must contain RoiSet.zip,
#' experiment.txt, and Results.xls. Most likely it will
#' also contain a list of numerous TIF files time-stamped
#' with filenames equal to epoch seconds.
#' 
#' @param folder path to the time series folder.
#' @return True if it worked, False if error.
#' @export
#' @examples
#' roi_folder_process("/path/to/ROI/folder/")
roi_folder_process <- function(folder){
	folder=normalizePath(folder)
	message(" -- Analyzing ROI from folder: ",folder)
	
	# make sure our folder has what we need
	roi_folder_check_files(folder)
	
	# load data from results file
	results.dt <- roi_read_results(file.path(folder, "Results.xls"))
	print(results.dt[1:5,])
	
	# next try to get baseline and drug times from experiment.txt
	
	# try to get time values from file names or experiment.txt
	
	# calculate dF/F
	
	return(results.dt)
}