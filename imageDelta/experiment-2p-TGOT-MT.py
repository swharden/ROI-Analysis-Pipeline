"""
Analysis of two-photon time-series data (filenames do not contain date codes)
"""

import os
import imageDelta as id

if __name__ == "__main__":
    folderPath = R"X:\Data\OT-Cre\OT-GCaMP intrinsic\190128-821693\TSeries-01282019-1332-1404"
    print(f"\n\nANALYZING: {folderPath}")
    drugs = []
    drugs.append(id.Drug("TGOT", id.drugFrameFromFileList(5, folderPath), durationFrames=60*3, padFrames=30))
    drugs.append(id.Drug("MT", id.drugFrameFromFileList(15, folderPath), durationFrames=60*3, padFrames=30))
    id.graphDrugExperiment(drugs, folderPath)
    print("DONE")