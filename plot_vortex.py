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
import scipy.interpolate as spi
import utilities as utilities


# ========================================================================
#
# Some defaults variables
#
# ========================================================================
plt.rc("text", usetex=True)
plt.rc("figure", max_open_warning=100)
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


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="A simple plot tool for vortex quantities"
    )
    parser.add_argument("-s", "--show", help="Show the plots", action="store_true")
    args = parser.parse_args()

    # Setup
    ninterp = 200
    mm2ft = 0.003_281
    mm2m = 1e-3
    fdir = os.path.abspath("SST-12")
    yname = os.path.join(fdir, "mcalister.yaml")
    fname = "avg_slice.csv"
    sdirs = ["vortex_slices"]
    labels = ["SST-12"]
    num_figs = 3

    # simulation setup parameters
    u0, v0, w0, umag0, rho0, mu = utilities.parse_ic(yname)
    aoa, baseline_aoa = utilities.parse_angle(fdir)
    chord = 1

    # experimental values
    edir = os.path.abspath(os.path.join("exp_data", f"aoa-{aoa}"))
    exp_xslices = utilities.get_vortex_slices()

    # Loop on data directories
    for i, sdir in enumerate([os.path.join(fdir, sdir) for sdir in sdirs]):

        # Read in data
        df = pd.read_csv(os.path.join(sdir, fname), delimiter=",")
        renames = {
            "Points:0": "x",
            "Points:1": "y",
            "Points:2": "z",
            "iblank": "iblank",
            "absIBlank": "absIBlank",
            "pressure": "p",
            "velocity_:0": "ux",
            "velocity_:1": "uy",
            "velocity_:2": "uz",
            "time": "avg_time",
        }
        df.columns = [renames[col] for col in df.columns]

        # Lineout through vortex core in each slice
        xslices = np.unique(df["x"])
        for k, xslice in enumerate(xslices):
            subdf = df[df["x"] == xslice].copy()
            idx = subdf["p"].idxmin()
            ymin, ymax = np.min(subdf["y"]), np.max(subdf["y"])
            zmin, zmax = np.min(subdf["z"]), np.max(subdf["z"])

            # vortex center location
            yc = np.array([subdf["y"].loc[idx]])
            zc = np.array([subdf["z"].loc[idx]])

            # interpolate across the vortex core
            yline = np.linspace(ymin, ymax, ninterp)
            zline = np.linspace(zmin, zmax, ninterp)
            ux_yc = spi.griddata(
                (subdf["y"], subdf["z"]),
                subdf["ux"],
                (yc[:, None], zline[None, :]),
                method="cubic",
            )
            uy_yc = spi.griddata(
                (subdf["y"], subdf["z"]),
                subdf["uy"],
                (yc[:, None], zline[None, :]),
                method="cubic",
            )

            plt.figure(k * num_figs + 0)
            p = plt.plot(
                zline / chord,
                ux_yc[0, :] / umag0,
                ls="-",
                lw=2,
                color=cmap[i],
                label=labels[i],
            )
            p[0].set_dashes(dashseq[i])

            plt.figure(k * num_figs + 1)
            p = plt.plot(
                zline / chord, uy_yc[0, :] / umag0, ls="-", lw=2, color=cmap[i]
            )
            p[0].set_dashes(dashseq[i])

            # Plot contours
            if i == 0:
                yi = np.linspace(ymin, ymax, ninterp)
                zi = np.linspace(zmin, zmax, ninterp)

                vcols = ["ux", "uy", "uz"]
                subdf["magvel"] = np.sqrt(np.square(subdf[vcols]).sum(axis=1))

                vi = spi.griddata(
                    (subdf["y"], subdf["z"]),
                    subdf["magvel"],
                    (yi[None, :], zi[:, None]),
                    method="cubic",
                )

                plt.figure(k * num_figs + 2)
                CS = plt.contourf(zi, yi, vi.T, 15)
                plt.plot(zc, yc, "ok", ms=5)
                plt.plot(
                    zline, yc * np.ones(zline.shape), ls="--", lw=1, color=cmap[-1]
                )
                plt.colorbar()
                plt.xlim(zmin, zmax)
                plt.ylim(ymin, ymax)

            # Experimental data
            idx = exp_xslices[np.fabs(exp_xslices.xslice + 1 - xslice) < 1e-5].index[0]
            ux_ename = glob.glob(os.path.join(edir, "ux_*_{:d}.txt".format(idx)))[0]
            uy_ename = glob.glob(os.path.join(edir, "uz_*_{:d}.txt".format(idx)))[0]
            exp_ux_df = pd.read_csv(ux_ename, header=0, names=["z", "ux"])
            exp_uy_df = pd.read_csv(uy_ename, header=0, names=["z", "uy"])

            # Change units
            exp_ux_df["z"] = exp_ux_df["z"] * mm2m / chord + 3.3
            exp_uy_df["z"] = exp_uy_df["z"] * mm2m / chord + 3.3

            plt.figure(k * num_figs + 0)
            plt.plot(
                exp_ux_df["z"],
                exp_ux_df["ux"],
                ls="-",
                lw=1,
                color=cmap[-1],
                marker=markertype[0],
                mec=cmap[-1],
                mfc=cmap[-1],
                ms=6,
                label="Exp.",
            )

            plt.figure(k * num_figs + 1)
            plt.plot(
                exp_uy_df["z"],
                exp_uy_df["uy"],
                ls="-",
                lw=1,
                color=cmap[-1],
                marker=markertype[0],
                mec=cmap[-1],
                mfc=cmap[-1],
                ms=6,
                label="Exp.",
            )

    # Save plots
    fname = "vortex.pdf"
    with PdfPages(fname) as pdf:
        for k, xslice in enumerate(xslices):
            plt.figure(k * num_figs + 0)
            ax = plt.gca()
            plt.xlabel(r"$z/c$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$u_x/u_\infty$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            ax.set_xlim([zmin, zmax])
            ax.set_title(r"$x={0:.2f}$".format(xslice))
            legend = ax.legend(loc="best")
            plt.tight_layout()
            pdf.savefig(dpi=300)

            plt.figure(k * num_figs + 1)
            ax = plt.gca()
            plt.xlabel(r"$z/c$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$u_y/u_\infty$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            ax.set_xlim([zmin, zmax])
            ax.set_title(r"$x={0:.2f}$".format(xslice))
            plt.tight_layout()
            pdf.savefig(dpi=300)

            plt.figure(k * num_figs + 2)
            ax = plt.gca()
            plt.xlabel(r"$z/c$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$y/c$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            plt.tight_layout()
            ax.set_xlim([zmin, zmax])
            ax.set_ylim([ymin, ymax])
            ax.set_title(r"$x={0:.2f}$".format(xslice))
            plt.tight_layout()
            pdf.savefig(dpi=300)

    if args.show:
        plt.show()
