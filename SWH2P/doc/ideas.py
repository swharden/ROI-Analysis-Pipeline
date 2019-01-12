"""
how do I want to use this?
"""

import sys
sys.path.append('../../')
import roi2p


TS=roi2p.TSeries('X:/path/to/TSeries/folder')
    # converts TIF data to 3D .npy arrays and saves or loads them - TS.R, TS.G
        # calculates TG.GR (G/R)
        # predicts TG.DGR (dG/R) based on average intensity from baseline
    # loads any ROI zips found - TS.ROIs
    # loads experiment info from experiment.txt (optional)
        # "baseline 3:00-7:00"
        # "GABA 7:30-9:30"
        # "TGOT 12:22-15:45"