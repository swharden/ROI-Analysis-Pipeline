library("devtools")
# we start in ./package/dev/
setwd("../")
# now we are in ./package/
message("\n\n### GENERATING DOCUMENTATION ###")
devtools::document()
setwd("../")
# now we are in ./
#message("\n\n### INSTALLING PACKAGE ###")
#install("boshROI")
#message("\n\n### DONE! ###")