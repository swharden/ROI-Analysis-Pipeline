"""
This module creates ROI plots and heatmaps from CSVs created by ImageJ's Multi-Measure tool.
All options are configurable using command line arguments.
"""

import pathlib
import shutil
import argparse
import roi2p


def analyze(resultsFile: str, framePeriod: float,
            baseline: tuple, measure: tuple, measureName: str,
            heatmapLimit: float = None, heatmapColormap: str = 'seismic'):

    resultsFile = pathlib.Path(resultsFile).resolve()
    if (resultsFile.exists() == False):
        raise Exception(f"file does not exist: {resultsFile}")
    if (resultsFile.suffix != ".csv"):
        raise Exception(f"file must end in .csv (not {resultsFile.suffix})")
    outputFolderName = f"autoanalysis - {resultsFile.name[:-4]} - {measureName}"
    outputFolder = resultsFile.parent.joinpath(
        resultsFile.parent.joinpath(outputFolderName))
    if (outputFolder.exists()):
        input(f"press ENTER to delete old folder...")
        shutil.rmtree(outputFolder)
    outputFolder.mkdir()

    print(f"Analyzing {resultsFile.name}...")
    roi = roi2p.ROI(resultsFile, framePeriod, baseline, measure)

    print("Creating settings file...")
    roi.saveSettings(outputFolder.joinpath("settings.txt"))

    print("Creating mean ROI plot...")
    roi.plotRoisMean(saveAs=outputFolder.joinpath("dff-mean.png"))

    print("Creating response plots...")
    roi.plotResponseScatter(saveAs=outputFolder.joinpath("dff-responses.png"))

    print("Creating heatmaps...")
    roi.plotHeatmap(
        saveAs=outputFolder.joinpath("dff-heatmap.png"),
        percentLimit=heatmapLimit,
        colormap=heatmapColormap)
    roi.saveCsv(outputFolder.joinpath("dff.csv"))

    print("Analysis Complete")
    return


def scottTest():
    resultsFile = R"C:\Users\swharden\Documents\important\2021-04-13 NG GCaMP\roi\45-LNG_distension 2 and 3_RoiSet.csv"
    shutil.rmtree(
        R"C:\Users\swharden\Documents\important\2021-04-13 NG GCaMP\roi\autoanalysis - 45-LNG_distension 2 and 3_RoiSet")
    analyze(resultsFile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--results', help='ROI results file created by ImageJ',
                        type=str, required=True, metavar="FilePath")

    parser.add_argument('--period', help='Time (seconds) between the start of successive frames',
                        type=float, required=True, metavar="FramePeriod")

    parser.add_argument('--b1', help='Start of the baseline period (seconds)',
                        type=float, required=True, metavar="BaselineStart")

    parser.add_argument('--b2', help='End of the baseline period (seconds)',
                        type=float, required=True, metavar="BaselineEnd")

    parser.add_argument('--m1', help='Start of the response measurement period (seconds)',
                        type=float, required=True, metavar="MeasureStart")

    parser.add_argument('--m2', help='End of the response measurement period (seconds)',
                        type=float, required=True, metavar="MeasureEnd")

    parser.add_argument('--name', help='Name for this measurement range',
                        type=str, required=True, metavar="Name")

    parser.add_argument('--colormap', help='Colormap to use for heatmaps',
                        type=str, required=False, metavar="Name", default="turbo")

    parser.add_argument('--limit', help='Define absolute limit (percent) for heatmaps to center them at zero',
                        type=float, required=False, metavar="Percent")

    args = parser.parse_args()

    analyze(resultsFile=args.results,
            framePeriod=args.period,
            baseline=(args.b1, args.b2),
            measure=(args.m1, args.m2),
            measureName=args.name,
            heatmapLimit=args.limit,
            heatmapColormap=args.colormap)
