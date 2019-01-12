// to use this, drag/drop it over FIJI (ImageJ)
// then drag/drop a whole TSeries folder onto ImageJ (uncheck all boxes)
// a single stack will open in grayscale. 
// select this script and run it (ctrl+R) to make it a magenta/green movie.

rename("splitme");
run("Stack Splitter", "number=2");
selectWindow("stk_0001_splitme");rename("splitme_R");
selectWindow("stk_0002_splitme");rename("splitme_G");
run("Merge Channels...", "c2=splitme_G c6=splitme_R create");