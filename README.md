# ROI Analysis Pipeline
This project contains Python scripts and R packages written to facilitate analysis of fluorescent micrographs for the purpose of biomedical research. Although code in this project can be interacted with directly for the purpose of data exploration, care is taken to ensure these scripts can also be run in a fully-automated manner allowing them to serve as individual component in a data analysis pipeline or be executed by a web-based data browsing front-end (i.e., [SWHLabPHP](https://github.com/swharden/SWHLabPHP)). Data analyzed by these routines are typically related to calcium reporting fluorophores (i.e., Fluo-4, Fluo-4 AM, Fluo-5, GCaMP6) obtained with a traditional epifluroesecnce or two-photon scanning laser microscope.

These projects are collaboratively written and maintained by [Scott Harden](https://github.com/swharden) and [Beronica Ocasio](https://github.com/beronicao).

Project | Description
---|---
**[boshROI](boshROI)** | R Package designed to analyze cellular calcium signals (reported by GCaMP6f) from a time series of single-channel micrographs. ImageJ is used to draw regions of interest (ROIs), and this script loads the ROIs, analyzes the TIFs (using different image analysis methods), and generates delta F / F graphs. 
**[pyROI](pyROI)** | Python scripts to generate annotated video (showing ROIs and graphs of analyzed data) from ROI data. Video output is HTML5-compatible MP4. Code here supplements boshROI.
**[bosh2P](bosh2P)**  | R Package designed to analyze sub-cellular calcium transients in neurons from two-photon linescans simultaneously imaging Fluo-5f and Alexa Fluor 594. Calcium fluctuations are reported as the ratio of these two fluorophores.
**[pyLS](pyLS)** | Python scripts to generate dF/F graphs from linescan data. Code here is independent of (but complementary to) boshLS.

Screenshots
![](pyLS/screenshot.png)

![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_01_img.png)

![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_02_avg.png)

![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_03_drift1.png)

![](/data/linescan/realistic/LineScan-06162017-1223-636/analysis/fig_04_drift2.png)
