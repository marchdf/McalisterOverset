#
# Run this script on NERSC Edison with something like:
#    start_pvbatch.sh 4 4 00:10:00 default debug `pwd`/pp_vortex.py
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

odir = os.path.abspath("./DES/vortex_slices")
shutil.rmtree(odir, ignore_errors=True)
os.makedirs(odir)
oname = os.path.join(odir, "output.csv")

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'ExodusIIReader'
exoreader = ExodusIIReader(FileName=fnames)
exoreader.PointVariables = ["iblank", "pressure", "velocity_"]
exoreader.SideSetArrayStatus = []
exoreader.ElementBlocks = [
    "nearbody-hex",
    "nearbody-wedge",
    "tipvortex-hex",
    "tipvortex-wedge",
    "farwake-hex",
    "farwake-tetra",
    "farwake-wedge",
    "farwake-pyramid",
]

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

# create a new 'Slice'
slice1 = Slice(Input=threshold1)
slice1.SliceType = "Plane"
slice1.SliceOffsetValues = slice_locations.get_vortex_slices()

# init the 'Plane' selected for 'SliceType'
slice1.SliceType.Origin = [1.0, 0.0, 0.0]

# create a new 'Clip'
clip1 = Clip(Input=slice1)
clip1.ClipType = "Plane"
clip1.Scalars = ["POINTS", "pressure"]

# init the 'Plane' selected for 'ClipType'
clip1.ClipType.Origin = [0.0, -1.0, 0.0]
clip1.ClipType.Normal = [0.0, -1.0, 0.0]

# create a new 'Clip'
clip2 = Clip(Input=clip1)
clip2.ClipType = "Plane"
clip2.Scalars = ["POINTS", "pressure"]

# init the 'Plane' selected for 'ClipType'
clip2.ClipType.Origin = [0.0, 1.0, 0.0]
clip2.ClipType.Normal = [0.0, 1.0, 0.0]

# create a new 'Clip'
clip3 = Clip(Input=clip2)
clip3.ClipType = "Plane"
clip3.Scalars = ["POINTS", "pressure"]

# init the 'Plane' selected for 'ClipType'
clip3.ClipType.Origin = [0.0, 0.0, 2.3]
clip3.ClipType.Normal = [0.0, 0.0, -1.0]

# create a new 'Clip'
clip4 = Clip(Input=clip3)
clip4.ClipType = "Plane"
clip4.Scalars = ["POINTS", "pressure"]

# init the 'Plane' selected for 'ClipType'
clip4.ClipType.Origin = [0.0, 0.0, 4.3]
clip4.ClipType.Normal = [0.0, 0.0, 1.0]


# ----------------------------------------------------------------
# save data
# ----------------------------------------------------------------
SaveData(
    oname,
    proxy=clip4,
    Precision=5,
    UseScientificNotation=0,
    WriteTimeSteps=1,
    FieldAssociation="Points",
)
