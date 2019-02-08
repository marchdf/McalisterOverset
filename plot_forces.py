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
# Main
#
# ========================================================================
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description="A simple plot tool for wing forces")
    parser.add_argument("-s", "--show", help="Show the plots", action="store_true")
    parser.add_argument(
        "-f", "--folder", help="Folder where files are stored", type=str, required=True
    )
    args = parser.parse_args()

    # Setup
    fdir = os.path.abspath(args.folder)
    yname = os.path.join(fdir, "mcalister.yaml")
    oname = os.path.join(fdir, "forces.dat")
    df = pd.read_csv(oname, delim_whitespace=True)

    area = 1.0 * 6.6
    u0, v0, w0, umag0, rho0, mu = utilities.parse_ic(yname)
    dynPres = rho0 * 0.5 * (umag0 ** 2)
    aoa, baseline_aoa = utilities.parse_angle(args.folder)

    # Lift and drag
    alpha = np.radians(baseline_aoa - aoa)
    c, s = np.cos(alpha), np.sin(alpha)
    df["cl"] = ((df.Fpy + df.Fvy) * c + (df.Fpx + df.Fvx) * s) / (dynPres * area)
    df["cd"] = (-(df.Fpy + df.Fvy) * s + (df.Fpx + df.Fvx) * c) / (dynPres * area)

    # Experimental values
    edir = os.path.abspath(os.path.join("exp_data", f"aoa-{aoa}"))
    df_cl_cd = pd.read_csv(os.path.join(edir, "cl_cd.txt"), comment="#")
    cl_exp = df_cl_cd.cl.iloc[0]
    cd_exp = df_cl_cd.cd.iloc[0]

    fname = "wing_forces.pdf"
    with PdfPages(fname) as pdf:
        plt.figure(0)
        plt.plot(df.Time, df.cl, ls="-", lw=2, color=cmap[0])
        plt.plot([df.Time.min(), df.Time.max()], [cl_exp, cl_exp], lw=1, color=cmap[-1])
        ax = plt.gca()
        plt.xlabel(r"$t$", fontsize=22, fontweight="bold")
        plt.ylabel(r"$c_l$", fontsize=22, fontweight="bold")
        plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
        plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
        # plt.ylim([0.5, 1.5])
        plt.ylim([0.2, 0.4])
        plt.tight_layout()
        pdf.savefig(dpi=300)

        plt.figure(1)
        ax = plt.gca()
        plt.plot(df.Time, df.cd, ls="-", lw=2, color=cmap[0])
        plt.plot([df.Time.min(), df.Time.max()], [cd_exp, cd_exp], lw=1, color=cmap[-1])
        plt.xlabel(r"$t$", fontsize=22, fontweight="bold")
        plt.ylabel(r"$c_d$", fontsize=22, fontweight="bold")
        plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
        plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
        # plt.ylim([0.02, 0.1])
        plt.ylim([0.0, 0.1])
        plt.tight_layout()
        pdf.savefig(dpi=300)

    if args.show:
        plt.show()
