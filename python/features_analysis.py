#!/usr/bin/env python3

import sys
import os
import os.path
import shutil
import numpy as np
import matplotlib.pyplot as plt
from view_angle import __file__ as va_filename

def base_plot(figsize=(8,4)):
    f = plt.figure(figsize=figsize)
    ax = f.add_subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    return f, ax

def match_angle(matches, shape):
    """Angle of the line connecting two matches
    when putting the two images side by side"""

    x1, y1, x2, y2 = matches[:,0], matches[:,1], matches[:,2], matches[:,3]
    return (180.0/np.pi)*np.arctan((y2 - y1) / (x2 - x1 + shape[1]))

def distances_plot(path, sorted_matches):
    f, ax = base_plot()
    ax.plot(sorted_matches[:,4])
    ax.set_xlabel("Match number (by distance)")
    ax.set_ylabel("Distance")
    f.savefig(path, bbox_inches='tight')
    plt.close(f)

def angle_spread_plot(path, angles):
    f, ax = base_plot()
    ax.plot(angles)
    ax.set_ylim([-3, 3])
    f.savefig(path, bbox_inches='tight')
    plt.close(f)

def spatial_coverage_plot(path, matches, image_shape):
    N = matches.shape[0]
    count = int(np.sqrt(N))
    # Number of points in grid cells
    areas = np.zeros((count, count))
    cell_size = image_shape / count
    coverage = np.zeros(N)
    for (i, (x1, y1, x2, y2, dist)) in enumerate(matches):
        # Euclidian division to get cell coordinate
        # Only consider image 1 keypoints
        areas[y1 // cell_size[0], x1 // cell_size[1]] += 1
        coverage[i] = np.sum(areas.flatten() > 0) / areas.size

    f, ax = base_plot()
    ax.plot(100 * coverage)

    ax.set_ylim([0, 100])
    ax.set_xlabel("Match number (by distance)")
    ax.set_ylabel("Spatial coverage (%)")

    f.savefig(path, bbox_inches='tight')
    plt.close(f)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./features_analysis.py <dir>")
        sys.exit(-1)

    # Produce plots for all directories containing matches.txt
    path = sys.argv[1]
    for root, subdirs, files in os.walk(path):
        if "matches.txt" in files:
            print("features_analysis.py: " + root)
            shape = np.loadtxt(os.path.join(root, "shape.txt"))
            matches = np.loadtxt(os.path.join(root, "matches.txt"), comments="#")

            # Distances plot
            distances_plot(os.path.join(root, "plot_distances.pdf"), matches)

            # Angle spread plot
            angles = match_angle(matches, shape)
            angle_spread_plot(os.path.join(root, "plot_angle_spread.pdf"), angles)

            # Spatial coverage plot
            spatial_coverage_plot(os.path.join(root, "plot_spatial_coverage.pdf"), matches, shape)

            # Copy view_angle_script.py
            shutil.copy(va_filename, root)

            # Create empty outlier_threshold.txt unless it exists
            otf = os.path.join(root, "outlier_threshold.txt")
            if not os.path.isfile(otf):
                f = open(otf, "w")
                f.write(" ")
                f.close()
