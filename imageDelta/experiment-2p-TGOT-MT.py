"""
Analysis of two-photon time-series data (filenames do not contain date codes)
"""

import os
import imageDelta as id

if __name__ == "__main__":
    folderPath = R"X:\Data\OTR-Cre\GCaMP6f PFC injection patch and linescan\2019-02-13\slice2\TSeries-02132019-1317-1418"
    print(f"\n\nANALYZING: {folderPath}")
    drugs = []

    # use frame numbers when working with two-photon time series
    drugs.append(id.Drug("TGOT", 98, durationFrames=20, padFrames=5))

    # use time-encoded filenames when dealing with LED images
    #drugs.append(id.Drug("TGOT", id.drugFrameFromFileList(10, folderPath), durationFrames=60*3, padFrames=30))
    #drugs.append(id.Drug("MT", id.drugFrameFromFileList(20, folderPath), durationFrames=60*3, padFrames=30))

    id.graphDrugExperiment(drugs, folderPath)
    print("DONE")