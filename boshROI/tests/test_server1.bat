:: use rscript to launch run.R from Windows
@echo off
cls
set PATH=%PATH%;"C:\Program Files\R\R-3.4.0\bin"
rscript --vanilla ../R/server.R --analyzeRoiFolder "X:\Data\SCOTT\2017-05-10 GCaMP6f\2017-05-10 GCaMP6f PFC OXTR cre\2017-06-01 cell3"