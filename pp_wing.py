#
# Run this script on NERSC Edison with something like:
#    start_pvbatch.sh 4 4 00:10:00 default debug `pwd`/pp_wing.py
#


# ----------------------------------------------------------------
# imports
# ----------------------------------------------------------------
# import the simple module from the paraview
from paraview.simple import *

# disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

import os
import glob
import shutil
import slice_locations as slice_locations

# ----------------------------------------------------------------
# setup
# ----------------------------------------------------------------

# Get file names
fdir = os.path.abspath("./DES/out")
pattern = "*.e.*"
fnames = sorted(glob.glob(os.path.join(fdir, pattern)))

odir = os.path.abspath("./DES/wing_slices")
shutil.rmtree(odir, ignore_errors=True)
os.makedirs(odir)
oname = os.path.join(odir, "output.csv")

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'ExodusIIReader'
exoreader = ExodusIIReader(FileName=fnames)
exoreader.PointVariables = [
    "iblank",
    "pressure",
    "pressure_force_",
    "tau_wall",
    "velocity_",
]
exoreader.NodeSetArrayStatus = []
exoreader.SideSetArrayStatus = ["wing"]
exoreader.ElementBlocks = []

# get active view
renderView1 = GetActiveViewOrCreate("RenderView")

# create a new 'Calculator'
calculator1 = Calculator(Input=exoreader)
calculator1.ResultArrayName = "absIBlank"
calculator1.Function = "abs(iblank)"

# create a new 'Threshold'
threshold1 = Threshold(Input=calculator1)
threshold1.Scalars = ["POINTS", "absIBlank"]
threshold1.ThresholdRange = [1.0, 1.0]

# wing properties
wing_length = 3.3

# create a new 'Slice'
# at span location corresponding to McAlister paper Fig. 21
slice1 = Slice(Input=threshold1)
slice1.SliceType = "Plane"
slice1.SliceOffsetValues = slice_locations.get_wing_slices()

# init the 'Plane' selected for 'SliceType'
slice1.SliceType.Origin = [0.0, 0.0, 0.0]
slice1.SliceType.Normal = [0.0, 0.0, 1.0]

# ----------------------------------------------------------------
# save data
# ----------------------------------------------------------------
SaveData(
    oname,
    proxy=slice1,
    Precision=5,
    UseScientificNotation=0,
    WriteTimeSteps=1,
    FieldAssociation="Points",
)
