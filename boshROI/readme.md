# BOSH ROI
BOSH ROI is an R Package developed assist in the analysis of calcium reporting fluorophores (i.e., FluoAM, Fluo-4 and GCaMP6) from time series images analyzed in [NIH ImageJ](https://imagej.nih.gov/ij/index.html) / [FIJI](http://fiji.sc/). The BOSH ROI package was initially developed by Beronica Ocasio and Scott Harden.

## Installing
To generate documentation and install the boshROI package:
* `cd ./dev/`
* `rscript install.R`

## Uninstalling
* `rscript -e remove.packages(boshROI)`

# Developer Notes

## R code base
R scripts here are maintained by Scott and Beronica. These scripts are designed to run "headless" from a server. They are written with modularization / code recycling as a priority. They are designed to be run with `RScript` and not interactively in RStudio.

## Setup
This section includes notes for setting up a developer environment to edit/run R scripts. RStudio is great for interactive testing, but I'd like to develop exclusively with `RScript.exe` since that's what the server will be calling.

## System Path
If you want to be able to type `rscript` in a command window, you have to edit the system environment variables to add the R/bin/ folder (containing RScript.exe) to your system PATH. On my computer it was `C:\Program Files\R\R-3.4.0\bin\`

## Notepad++
I like to edit code in Notepad++ and press F5 to run it. This is the F5 command I use: `"C:\Program Files\R\R-3.4.0\bin\Rscript.exe" --vanilla "$(FULL_CURRENT_PATH)" & pause`