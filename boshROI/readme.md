# BOSH ROI
BOSH ROI is an R Package developed assist in the analysis of calcium reporting fluorophores (i.e., FluoAM, Fluo-4 and GCaMP6) from time series images analyzed in [NIH ImageJ](https://imagej.nih.gov/ij/index.html) / [FIJI](http://fiji.sc/). The BOSH ROI package was initially developed by Beronica Ocasio and Scott Harden.

## Installing
To install the latest boshROI package version from GitHub, use these commands:
```R
install.packages("devtools")
library(devtools)
devtools::install_github("swharden/ROI-Analysis-Pipeline", subdir = "boshROI" )
library(boshROI)
```

## Uninstalling
```R
remove.packages("boshROI")
```

## Updating
```R
library(devtools)
update_packages("boshROI")
```

