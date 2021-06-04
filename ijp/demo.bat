:: Basic analysis with default settings
python analyze.py --period 1.0 --b1 30 --b2 50 --m1 60 --m2 80 --name "stimulus 1" ^
--results "C:\Users\swharden\Documents\important\2021-04-13 NG GCaMP\roi\45-LNG_distension 2 and 3_RoiSet.csv"

:: For multiple stimuli, change the measurement range and name
python analyze.py --period 1.0 --b1 30 --b2 50 --m1 90 --m2 110 --name "stimulus 2" ^
--results "C:\Users\swharden\Documents\important\2021-04-13 NG GCaMP\roi\45-LNG_distension 2 and 3_RoiSet.csv"

:: This example uses an alternate colormap
:: https://matplotlib.org/stable/tutorials/colors/colormaps.html
python analyze.py --period 1.0 --b1 30 --b2 50 --m1 60 --m2 80 --name "colormap-viridis" --colormap "viridis" ^
--results "C:\Users\swharden\Documents\important\2021-04-13 NG GCaMP\roi\45-LNG_distension 2 and 3_RoiSet.csv"

:: This example uses a balanced colormap (no change or zero dF/F is white). Balanced colormaps require defined limits.
python analyze.py --period 1.0 --b1 30 --b2 50 --m1 60 --m2 80 --name "colormap-balanced" --colormap "seismic" --limit 150 ^
--results "C:\Users\swharden\Documents\important\2021-04-13 NG GCaMP\roi\45-LNG_distension 2 and 3_RoiSet.csv"