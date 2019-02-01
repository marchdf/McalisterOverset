#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import utilities as utilities

# ========================================================================
#
# Some defaults variables
#
# ========================================================================
plt.rc("text", usetex=True)
cmap_med = [
    "#F15A60",
    "#7AC36A",
    "#5A9BD4",
    "#FAA75B",
    "#9E67AB",
    "#CE7058",
    "#D77FB4",
    "#737373",
]
cmap = [
    "#EE2E2F",
    "#008C48",
    "#185AA9",
    "#F47D23",
    "#662C91",
    "#A21D21",
    "#B43894",
    "#010202",
]
dashseq = [
    (None, None),
    [10, 5],
    [10, 4, 3, 4],
    [3, 3],
    [10, 4, 3, 4, 3, 4],
    [3, 3],
    [3, 3],
]
markertype = ["s", "d", "o", "p", "h"]


# ========================================================================
#
# Function definitions
#
# ========================================================================
def sort_by_angle(x, y, var):
    """Radial sort of variable on x and y for plotting

    Inspired from:
    http://stackoverflow.com/questions/35606712/numpy-way-to-sort-out-a-messy-array-for-plotting

    """

    # Get the angle wrt the mean of the cloud of points
    x0, y0 = x.mean(), y.mean()
    angle = np.arctan2(y - y0, x - x0)

    # Sort based on this angle
    idx = angle.argsort()
    idx = np.append(idx, idx[0])

    return x[idx], y[idx], var[idx]


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == "__main__":

    # ========================================================================
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="A simple plot tool for wing quantities"
    )
    parser.add_argument("-s", "--show", help="Show the plots", action="store_true")
    args = parser.parse_args()

    # ========================================================================
    # Setup
    fdir = os.path.abspath("DES")
    yname = os.path.join(fdir, "mcalister.yaml")
    fname = "avg_slice.csv"
    sdirs = ["wing_slices"]
    labels = ["DES"]

    # simulation setup parameters
    u0, rho0, mu = utilities.parse_ic(yname)
    chord = 1

    # ========================================================================
    # Loop on data directories
    for i, sdir in enumerate([os.path.join(fdir, sdir) for sdir in sdirs]):

        # ========================================================================
        # Read in data
        df = pd.read_csv(os.path.join(sdir, fname), delimiter=",")
        renames = {
            "Points:0": "x",
            "Points:1": "y",
            "Points:2": "z",
            "pressure": "p",
            "iblank": "iblank",
            "absIBlank": "absIBlank",
            "pressure_force_:0": "fpx",
            "pressure_force_:1": "fpy",
            "pressure_force_:2": "fpz",
            "tau_wall": "tau_wall",
            "velocity_:0": "ux",
            "velocity_:1": "uy",
            "velocity_:2": "uz",
            "time": "avg_time",
        }
        df.columns = [renames[col] for col in df.columns]

        # Calculate the negative of the surface pressure coefficient
        df["cp"] = -df["p"] / (0.5 * rho0 * u0 ** 2)

        # ========================================================================
        # Plot cp in each slice
        zslices = np.unique(df["z"])

        for k, zslice in enumerate(zslices):
            subdf = df[df["z"] == zslice]

            # Sort for a pretty plot
            x, y, cp = sort_by_angle(
                subdf["x"].values, subdf["y"].values, subdf["cp"].values
            )

            # plot
            plt.figure(k)
            ax = plt.gca()
            p = plt.plot(x / chord, cp, ls="-", lw=2, color=cmap[i], label=labels[i])
            p[0].set_dashes(dashseq[i])

    # ========================================================================
    # Save plots
    fname = "wing_cp.pdf"
    with PdfPages(fname) as pdf:

        for k, zslice in enumerate(zslices):
            plt.figure(k)
            ax = plt.gca()
            plt.xlabel(r"$x/c$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$-c_p$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            plt.xlim([0, chord])
            plt.ylim([-1.5, 4.5])
            ax.set_title(r"$z={0:.5f}$".format(zslice))
            plt.tight_layout()
            if k == 1:
                legend = ax.legend(loc="best")
            pdf.savefig(dpi=300)

    if args.show:
        plt.show()
