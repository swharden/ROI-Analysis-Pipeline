"""
Code in this file aims to automatically produce "difference images" from 
full frame micrographs of calcium-sensitive fluorophores before and after a drug
is applied. This is done by creating a baseline image (the average of several
TIFs before the drug) and calculating the difference between that and the average
image of the drug exposure. The difference is color-coded where no change is white,
decrease in brightness is blue, an dincrease in brightness is red.
"""

import os
import imageDelta as id

if __name__ == "__main__":

    ### CUSTOM ANALYSIS ###
    # This sample analysis routine analyzes all experiments where drugs were applied at the same time.
    # To create a new experiment, re-write this portion of the code.

    # given a list of experiment folders, analyze only those with NaCl in the filename
    folderRoot = R"X:\Data\AT1-Cre\MPO GCaMP6f\data\data-epi"    
    folders = sorted(os.listdir(folderRoot))
    folders = [x for x in folders if "-NaCl" in x]
    folders = [os.path.join(folderRoot, x) for x in folders]

    # ensure experiment folders contain properly-formatted filenames
    for folder in folders:
        folderPath = os.path.join(folder,"video")
        id.ensureImageFilenamesAreNumbers(folderPath)

    # analyze each experiment folder
    for folder in folders:
        folderPath = os.path.join(folder,"video")
        print(f"\n\nANALYZING: {folderPath}")
        drugs = []
        drugs.append(id.Drug("NaCl", id.drugFrameFromFileList(10, folderPath)))
        drugs.append(id.Drug("AngII", id.drugFrameFromFileList(20, folderPath)))
        id.graphDrugExperiment(drugs, folderPath)
    
    print("DONE")