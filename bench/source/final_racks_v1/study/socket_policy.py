"""Owner's 2026-10-09 shaft-location contract; lengths along the shaft, in mm."""
MIN_GUIDE_MM=40.
GUIDE_SIZE_RATIO=8.
ENTRY_LEAD_MM=3.
ENTRY_WIDTH_PER_FLAT_MM=1.5
VENT_DIAMETER_MM=1.
HEX_CLEARANCE_PER_FLAT_MM=.19
HANDLE_AXIS='flats'


def guide_length(shaft_size_mm):
    size=float(shaft_size_mm)
    if size<=0:raise ValueError('shaft size must be positive')
    return max(MIN_GUIDE_MM,GUIDE_SIZE_RATIO*size)


def burial_depth(shaft_size_mm):
    return guide_length(shaft_size_mm)+ENTRY_LEAD_MM
