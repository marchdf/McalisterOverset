# ========================================================================
def get_wing_slices():
    """Return the wing slices at span location corresponding to McAlister paper Fig. 21"""
    half_wing_length = 3.3
    slices = [
        0.994,
        0.974,
        0.944,
        0.899,
        0.843,
        0.773,
        0.692,
        0.597,
        0.490,
        0.370,
        0.238,
        0.094,
    ]
    return [half_wing_length * x for x in slices]


# ========================================================================
def get_vortex_slices():
    """Return the vortex slices"""
    return [0.1, 0.2, 0.5, 1.0, 2.0, 4.0, 6.0]
