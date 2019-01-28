"""
Analysis of two-photon time-series data (filenames do not contain date codes)
"""

import os
import imageDelta as id

if __name__ == "__main__":

    ### CUSTOM ANALYSIS ###
    # This sample analysis routine analyzes all experiments where drugs were applied at the same time.
    # To create a new experiment, re-write this portion of the code.

    # given a list of experiment folders, analyze only the TSeries
    folderRoot = R"X:\Data\OT-Cre\OT-GCaMP intrinsic\190128-821693"
    folders = sorted(os.listdir(folderRoot))
    folders = [x for x in folders if x.startswith("TSeries-")]
    folders = [os.path.join(folderRoot, x) for x in folders]

    # analyze each experiment folder
    for folder in folders:
        folderPath = os.path.join(folderRoot, folder)
        print(f"\n\nANALYZING: {folderPath}")
        drugs = []
        drugs.append(id.Drug("TGOT", id.drugFrameFromFileList(10, folderPath), durationFrames=60*3, padFrames=30))
        drugs.append(id.Drug("MT", id.drugFrameFromFileList(20, folderPath), durationFrames=60*3, padFrames=30))
        id.graphDrugExperiment(drugs, folderPath)
    
    print("DONE")