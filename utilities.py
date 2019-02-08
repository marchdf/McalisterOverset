# ========================================================================
#
# Imports
#
# ========================================================================
import re
import numpy as np
import pandas as pd
import yaml
import slice_locations as slice_locations


# ========================================================================
#
# Function definitions
#
# ========================================================================
def get_merged_csv(fnames, **kwargs):
    lst = []
    for fname in fnames:
        try:
            df = pd.read_csv(fname, **kwargs)
            lst.append(df)
        except pd.io.common.EmptyDataError:
            pass
    return pd.concat(lst, ignore_index=True)


# ========================================================================
def parse_ic(fname):
    """Parse the Nalu yaml input file for the initial conditions"""
    with open(fname, "r") as stream:
        try:
            dat = yaml.load(stream)
            u0 = float(
                dat["realms"][0]["initial_conditions"][0]["value"]["velocity"][0]
            )
            v0 = float(
                dat["realms"][0]["initial_conditions"][0]["value"]["velocity"][1]
            )
            w0 = float(
                dat["realms"][0]["initial_conditions"][0]["value"]["velocity"][2]
            )
            umag = np.sqrt(u0 ** 2 + v0 ** 2 + w0 ** 2)
            rho0 = float(
                dat["realms"][0]["material_properties"]["specifications"][0]["value"]
            )
            mu = float(
                dat["realms"][0]["material_properties"]["specifications"][1]["value"]
            )
            return u0, v0, w0, umag, rho0, mu

        except yaml.YAMLError as exc:
            print(exc)


# ========================================================================
def parse_angle(fdir):
    """Parse the angle of attack from the folder name"""
    return int(re.search(r"\d+", fdir).group()), 12.0


# ========================================================================
def get_wing_slices():
    """Return the wing slices"""
    return pd.DataFrame(slice_locations.get_wing_slices(), columns=["zslice"])


# ========================================================================
def get_vortex_slices():
    """Return the vortex slices"""
    return pd.DataFrame(slice_locations.get_vortex_slices(), columns=["xslice"])
