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
import scipy.interpolate as spi
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


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == "__main__":

    # ========================================================================
    # Parse arguments
    # ========================================================================
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="A simple plot tool for vortex quantities"
    )
    parser.add_argument("-s", "--show", help="Show the plots", action="store_true")
    args = parser.parse_args()

    # ========================================================================
    # Setup
    ninterp = 200
    mm2ft = 0.003281
    fdir = os.path.abspath("DES")
    yname = os.path.join(fdir, "mcalister.yaml")
    fname = "avg_slice.csv"
    sdirs = ["vortex_slices"]
    labels = ["DES"]
    num_figs = 3

    # simulation setup parameters
    u0, rho0, mu = utilities.parse_ic(yname)
    chord = 1

    # experimental values
    edir = os.path.abspath("exp_data")
    fux_exp = os.path.join(edir, "ux_x4.txt")
    fuz_exp = os.path.join(edir, "uz_x4.txt")

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
            "iblank": "iblank",
            "absIBlank": "absIBlank",
            "pressure": "p",
            "velocity_:0": "ux",
            "velocity_:1": "uy",
            "velocity_:2": "uz",
            "time": "avg_time",
        }
        df.columns = [renames[col] for col in df.columns]

        # ========================================================================
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
                ux_yc[0, :] / u0,
                ls="-",
                lw=2,
                color=cmap[i],
                label=labels[i],
            )
            p[0].set_dashes(dashseq[i])

            plt.figure(k * num_figs + 1)
            p = plt.plot(zline / chord, uy_yc[0, :] / u0, ls="-", lw=2, color=cmap[i])
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

    # # ========================================================================
    # # Experimental data
    # exp_ux_df = pd.read_csv(fux_exp, delimiter=",", header=0, names=["y", "ux"])
    # exp_uz_df = pd.read_csv(fuz_exp, delimiter=",", header=0, names=["y", "uz"])

    # # Shift in ft to align coordinates with mesh.
    # yshift = 0.0749174

    # exp_ux_df["y"] = (exp_ux_df["y"] * mm2ft - yshift) / chord
    # exp_uz_df["y"] = (exp_uz_df["y"] * mm2ft - yshift) / chord

    # plt.figure(0)
    # plt.plot(
    #     exp_ux_df["y"],
    #     exp_ux_df["ux"],
    #     ls="-",
    #     lw=1,
    #     color=cmap[-1],
    #     marker=markertype[0],
    #     mec=cmap[-1],
    #     mfc=cmap[-1],
    #     ms=6,
    #     label="Exp.",
    # )

    # plt.figure(1)
    # plt.plot(
    #     exp_uz_df["y"],
    #     exp_uz_df["uz"],
    #     ls="-",
    #     lw=1,
    #     color=cmap[-1],
    #     marker=markertype[0],
    #     mec=cmap[-1],
    #     mfc=cmap[-1],
    #     ms=6,
    # )

    # ========================================================================
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
