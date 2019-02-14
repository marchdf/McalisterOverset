#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
import glob as glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import utilities
import slice_locations

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

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="A simple plot tool for wing quantities"
    )
    parser.add_argument("-s", "--show", help="Show the plots", action="store_true")
    args = parser.parse_args()

    # Setup
    fdir = os.path.abspath("SST-12")
    yname = os.path.join(fdir, "mcalister.yaml")
    fname = "avg_slice.csv"
    sdirs = ["wing_slices"]
    labels = ["SST-12"]
    half_wing_length = slice_locations.get_half_wing_length()

    # simulation setup parameters
    u0, v0, w0, umag0, rho0, mu = utilities.parse_ic(yname)
    aoa, baseline_aoa = utilities.parse_angle(fdir)
    chord = 1

    # experimental values
    edir = os.path.abspath(os.path.join("exp_data", f"aoa-{aoa}"))
    exp_zslices = utilities.get_wing_slices()

    # data from other CFD simulations (SA model)
    sadir = os.path.abspath(os.path.join("sitaraman_data", f"aoa-{aoa}"))

    # Loop on data directories
    for i, sdir in enumerate([os.path.join(fdir, sdir) for sdir in sdirs]):

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

        # Project coordinates on to chord axis
        ang = np.radians(aoa)
        crdvec = np.array([np.cos(ang), -np.sin(ang)])
        rotcen = 0.25
        df["xovc"] = (
            np.dot(np.asarray([df.x - rotcen, df.y]).T, crdvec) / chord + rotcen
        )

        # Calculate the negative of the surface pressure coefficient
        df["cp"] = -df["p"] / (0.5 * rho0 * umag0 ** 2)

        # Plot cp in each slice
        zslices = np.unique(df["z"])

        for k, zslice in enumerate(zslices):
            subdf = df[df["z"] == zslice]

            # Sort for a pretty plot
            x, y, cp = sort_by_angle(
                subdf["xovc"].values, subdf["y"].values, subdf["cp"].values
            )

            # plot
            plt.figure(k)
            ax = plt.gca()
            p = plt.plot(x, cp, ls="-", lw=2, color=cmap[i], label=labels[i])
            p[0].set_dashes(dashseq[i])

            # Load corresponding exp data
            idx = exp_zslices[np.fabs(exp_zslices.zslice - zslice) < 1e-5].index[0]
            ename = glob.glob(os.path.join(edir, "cp_*_{:d}.txt".format(idx)))[0]
            exp_df = pd.read_csv(ename, header=0, names=["x", "cp"])
            plt.plot(
                exp_df.x,
                exp_df.cp,
                ls="",
                color=cmap[-1],
                marker=markertype[0],
                ms=6,
                mec=cmap[-1],
                mfc=cmap[-1],
                label="Exp.",
            )

            # Load corresponding SA data
            satname = os.path.join(
                sadir, "cp_{0:.3f}_top.csv".format(zslice / half_wing_length)
            )
            sabname = os.path.join(
                sadir, "cp_{0:.3f}_bot.csv".format(zslice / half_wing_length)
            )
            try:
                satop = pd.read_csv(satname)
                sabot = pd.read_csv(sabname)
            except FileNotFoundError:
                continue
            satop.sort_values(by=["x"], inplace=True)
            sabot.sort_values(by=["x"], inplace=True, ascending=False)
            plt.plot(
                np.concatenate((satop.x, sabot.x), axis=0),
                np.concatenate((satop.cp, sabot.cp), axis=0),
                ls="-",
                color=cmap[-2],
                label="Sitaraman et al. (2010)",
            )

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
            plt.ylim([-1.5, 5.5])
            ax.set_title(r"$z/s={0:.5f}$".format(zslice / half_wing_length))
            plt.tight_layout()
            if k == 0:
                legend = ax.legend(loc="best")
            pdf.savefig(dpi=300)

    if args.show:
        plt.show()
