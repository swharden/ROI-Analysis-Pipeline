# Programming Notes
Items in this folder are are notes created by the developers. Each folder contains an entirely self-suffecient collection of R scripts.

## Executing R Scripts
Since this project is mainly intended to be run by a headless server (called by `rscript`), development will primarially use notepad and rscript and rarely involve rstudio.

## Creating a Package
I created a package from the command line. I just opened up a console, navigated to the parent directory, and ran the following:

```
install.packages("devtools")
library("devtools")
create("boshPackage") # this created the ./boshPackage/ folder and filled it with stuff
```

```
remove.packages(boshROI)
```

Then go back in and edit the `DESCRIPTION` file to reflect what the package does.

### Adding Functions
create one R script per function (???) in the ./R/ folder. Use proper documentation formatting so it can be automatically documented later. **CRITICAL:** Without the proper comments, functions will not be added to the package. It seems the `@export` is the kicker, but you might as well thouroughly document as you go anyway.

### Generating Documentation
Roxygen2 does this from comments in the R source code.

```
devtools::document()
```

# Useful Links
* [ggplot2 cheat sheet](https://www.rstudio.com/wp-content/uploads/2015/03/ggplot2-cheatsheet.pdf)
* [r colors cheat sheet](https://www.nceas.ucsb.edu/~frazier/RSpatialGuides/colorPaletteCheatsheet.pdf)
* [example well maintained R package on GitHub](https://github.com/dirkschumacher/ompr)
* [data table cheat sheet](https://s3.amazonaws.com/assets.datacamp.com/img/blog/data+table+cheat+sheet.pdf)
* [plotting simple graphs in R](http://www.harding.edu/fmccown/r/)
* [R Language Definition](https://cran.r-project.org/doc/manuals/R-lang.html#Operators)
* [sprintf examples](http://www.cookbook-r.com/Strings/Creating_strings_from_variables/)
* [writing package documentation](https://support.rstudio.com/hc/en-us/articles/200532317-Writing-Package-Documentation)
* [making an R package from scratch](https://hilaryparker.com/2014/04/29/writing-an-r-package-from-scratch/)