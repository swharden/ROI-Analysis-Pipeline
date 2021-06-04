"""
This modules contains logic to analyze calcium levels from ROIs created by ImageJ's Multi-Measure tool
"""

from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pathlib
import datetime


class ROI:
    def __init__(self, resultsFile: pathlib.Path, framePeriod: float,
                 baselineTimes: Tuple, responseTimes: Tuple) -> None:
        """
        The ROI class contains common logic for working with ΔF/F data.

        resultsFile: CSV file created by ImageJ's ROI Multi-Measure
        prairieFile: XML file created by PrairieView
        baselineTimes: start and end (in time units) of F₀
        responseTimes: start and end (in time units) of the intervention
        """
        self.resultsFile = pathlib.Path(resultsFile)

        self.name = self.resultsFile.name
        self.baselineTimes = baselineTimes
        self.responseTimes = responseTimes

        rois = pd.read_csv(resultsFile)
        rois.drop(columns=rois.columns[0], axis=1, inplace=True)
        self.roiNames = rois.columns
        self.roiCount = rois.shape[1]

        self.framePeriod = framePeriod
        self.times = np.arange(len(rois)) * framePeriod
        self.baselineIndexes = (self.getIndexAfter(self.times, baselineTimes[0]),
                                self.getIndexAfter(self.times, baselineTimes[1]))
        self.responseIndexes = (self.getIndexAfter(self.times, responseTimes[0]),
                                self.getIndexAfter(self.times, responseTimes[1]))

        baselineIntensities = rois[self.baselineIndexes[0]                                   :self.baselineIndexes[1]]
        self.f0 = baselineIntensities.mean().values

        self.dff = (rois - self.f0) / self.f0 * 100
        self.dff = pd.DataFrame(self.dff)

        responseIntensities = self.dff[self.responseIndexes[0]                                       :self.responseIndexes[1]]
        self.responseMeans = responseIntensities.mean().values

    def getIndexAfter(self, times: np.ndarray, target: float) -> int:
        """Return the index of the times at or after the target time"""
        # TODO: argparse instead of assuming standard sample rate
        for thisIndex, thisTime in enumerate(times):
            if thisTime >= target:
                return int(thisIndex)
        return None

    def __repr__(self) -> str:
        return f"ΔF/F₀ data from '{self.resultsFile.name}' " +\
            f"with {self.dff.shape[1]} ROIs and {self.dff.shape[0]} time points"

    def shadeBaseline(self):
        plt.axvspan(self.baselineTimes[0],
                    self.baselineTimes[1],
                    color='b', alpha=.1)

    def shadeResponse(self):
        plt.axvspan(self.responseTimes[0],
                    self.responseTimes[1],
                    color='r', alpha=.1)

    def decoratePlot(self, baseline=True, measure=True):
        """Add standard labels, grid, spans, zero line, and tighten margins"""
        if (baseline):
            self.shadeBaseline()
        if (measure):
            self.shadeResponse()
        plt.ylabel("ΔF/F₀ (%)")
        plt.xlabel("Time (seconds)")
        plt.axhline(0, color='k', ls='--')
        plt.grid(alpha=.5, ls='--')
        plt.margins(x=0)
        plt.title(self.name)

    def plotRoisMean(self, color="k", label=None, saveAs=None, show=False):
        """Plot ΔF/F₀ mean +/- stdErr."""
        mean = self.dff.mean(axis=1)
        stdErr = self.dff.sem(axis=1)
        plt.fill_between(self.times, mean-stdErr, mean+stdErr,
                         color=color, alpha=.2)
        plt.plot(self.times, mean, color=color, label=label)
        self.decoratePlot()
        if saveAs:
            plt.savefig(saveAs)
        if show:
            plt.show()

    def plotRois(self):
        """Plot ΔF/F₀ for every ROI overlapping on a single plot."""
        for roi in self.dff:
            plt.plot(self.times, self.dff[roi])
        self.decoratePlot()

    def plotRoisIndividually(self, figsize=(6, 3), showAndClose=True):
        """Plot ΔF/F₀ for each ROI as an individual figure."""
        for roi in self.dff:
            plt.figure(figsize=figsize)
            plt.plot(self.times, self.dff[roi])
            self.decoratePlot()
            plt.title(roi)
            if showAndClose:
                plt.show()
                plt.close()

    def plotHeatmap(self, sort=False, percentLimit=None, colormap='seismic', saveAs=None, show=False):
        plt.figure(figsize=(10, 6))
        plt.xlabel("Time (sec)")
        plt.ylabel("ROI")
        plt.title(self.resultsFile.name)

        if sort:
            sortedIndexes = np.argsort(self.responseMeans)[::-1]
            data = self.dff.values[:, sortedIndexes].transpose()
        else:
            data = self.dff.transpose()

        plt.imshow(data,
                   extent=[0, self.dff.shape[0]*self.framePeriod,
                           self.dff.shape[1], 0],
                   cmap=plt.get_cmap(colormap),
                   interpolation='nearest', aspect='auto')

        cbar = plt.colorbar(label="ΔF/F (%)")

        if (percentLimit):
            plt.clim(-percentLimit, percentLimit)

        plt.axvline(self.baselineTimes[0], color='k', ls='--')
        plt.axvline(self.baselineTimes[1], color='k', ls='--')
        plt.axvline(self.responseTimes[0], color='k', ls='--')
        plt.axvline(self.responseTimes[1], color='k', ls='--')

        if saveAs:
            plt.savefig(saveAs)
        if show:
            plt.show()

    def plotResponseScatter(self, saveAs=None, show=False):
        plt.figure(figsize=(3, 6))
        plt.grid(alpha=.5, ls='--')
        plt.scatter(np.random.random_sample(self.dff.shape[1]),
                    self.responseMeans,
                    s=50, facecolors='none', edgecolors='C0', alpha=.8)
        plt.axhline(0, color='k', ls='--')
        plt.axis([-1, 2, None, None])
        plt.ylabel("Mean Response ΔF/F₀ (%) per ROI")
        plt.gca().xaxis.set_visible(False)
        plt.tight_layout()

        if saveAs:
            plt.savefig(saveAs)
        if show:
            plt.show()

    def saveSettings(self, filePath: str):
        lines = []
        lines.append(f"run on: {datetime.datetime.now()}")
        lines.append(f"source: {self.resultsFile}")
        lines.append(f"period: {self.framePeriod} (sec / frame)")
        lines.append(f"baseline: {self.baselineTimes}")
        lines.append(f"measurement: {self.responseTimes}")
        with open(filePath, 'w') as f:
            f.write("\n".join(lines))

    def saveCsv(self, filePath: str):
        """
        Time, Response, Roi1, Roi2, Roi3, ...
        """
        df = self.dff.copy()

        dffColumnNames = [x for x in self.roiNames]

        lines = []
        lines.append(",," + ",".join(dffColumnNames))
        lines.append(",Response (mean dF/F %)," +
                     ",".join([f"{x:.05f}" for x in self.responseMeans]))
        lines.append("")
        lines.append("Frame (#),Time (sec)," + ",".join(dffColumnNames))
        for i in range(self.dff.shape[0]):
            frameNumber = i + 1
            frameTime = i * self.framePeriod
            roiValues = ",".join([f"{x: .5f}" for x in self.dff.iloc[i]])
            lines.append(f"{frameNumber},{frameTime},{roiValues}")

        with open(filePath, 'w') as f:
            f.write("\n".join(lines))
