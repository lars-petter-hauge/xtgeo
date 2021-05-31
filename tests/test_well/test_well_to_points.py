import pytest

from xtgeo.well import Well
from xtgeo.common import XTGeoDialog

xtg = XTGeoDialog()

TMPD = xtg.tmpdir
TPATH = xtg.testpathobj

logger = xtg.basiclogger(__name__)

WFILE = TPATH / "wells/etc/otest.rmswell"


def string_to_well(fpath, wellstring, kwargs):
    """It is currently not possible to initiate from spec.
    We work around by dumping to csv before reloading
    """
    with open(fpath, "w") as fh:
        fh.write(wellstring)

    well = Well(fpath, **kwargs)

    return well


def test_wellzone_to_points():
    """Import well from file and put zone boundaries to a Pandas object."""

    mywell = Well(WFILE, zonelogname="Zone_model2", mdlogname="M_MDEPTH")

    # get the zpoints which is a Pandas
    zpoints = mywell.get_zonation_points(use_undef=False)
    assert zpoints.iat[9, 6] == 6

    # get the zpoints which is a Pandas
    zpoints = mywell.get_zonation_points(use_undef=True)
    assert zpoints.iat[9, 6] == 7

    with pytest.raises(ValueError):
        zpoints = mywell.get_zonation_points(zonelist=[1, 3, 4, 5])

    zpoints = mywell.get_zonation_points(zonelist=[3, 4, 5])
    assert zpoints.iat[6, 6] == 4

    zpoints = mywell.get_zonation_points(zonelist=(3, 5))
    assert zpoints.iat[6, 6] == 4


def test_wellzone_to_isopoints():
    """Import well from file and find thicknesses"""

    mywell = Well(WFILE, zonelogname="Zone_model2", mdlogname="M_MDEPTH")
    # get the zpoints which is a Pandas
    zpoints = mywell.get_zonation_points(use_undef=False, tops=True)
    assert zpoints["Zone"].min() == 3
    assert zpoints["Zone"].max() == 9

    zisos = mywell.get_zonation_points(use_undef=False, tops=False)
    assert zisos.iat[10, 8] == 4


def test_zonepoints_non_existing():
    pass


def test_zonepoints_to_points_compatibility():
    pass


def test_simple_points(tmp_path):

    wellstring = """1.01
Unknown
name 0 0 0
1
Zonelog DISC 1 zone1 2 zone2 3 zone2
1 2 3 1
4 5 6 2
7 8 9 3
"""
    fpath = tmp_path / "well.rmswell"
    kwargs = {"zonelogname": "Zonelog"}
    well = string_to_well(fpath, wellstring, kwargs)
    points = well.get_zonation_points(use_undef=False, tops=True, zonelist=[1, 2])
    # We are only getting a single point here, is that correct behaviour?
    # Unless the points are only supposed to be between zoness, I would expect two
    # Also occurs with a "nan" zone on the first row
    assert len(points) == 1
    assert (points["X_UTME"] == [4.0]).all
    assert (points["Y_UTME"] == [5.0]).all


def test_simple_points_two(tmp_path):

    wellstring = """1.01
Unknown
name 0 0 0
1
Zonelog DISC 1 zone1 2 zone2 3 zone3
0 0 0 nan
1 2 3 1
4 5 6 1
7 8 9 2
10 11 12 2
13 14 15 3
"""
    fpath = tmp_path / "well.rmswell"
    kwargs = {"zonelogname": "Zonelog"}
    well = string_to_well(fpath, wellstring, kwargs)
    points = well.get_zonation_points(use_undef=False, tops=True, zonelist=[1, 2, 3])
    assert len(points) == 2
    assert (points["X_UTME"] == [7.0, 14.0]).all
    assert (points["Y_UTMN"] == [8.0, 15.0]).all
    points = well.get_zonation_points(use_undef=False, tops=True, zonelist=[2, 3])
    assert len(points) == 2
    assert (points["X_UTME"] == [7.0, 14.0]).all
    assert (points["Y_UTMN"] == [8.0, 15.0]).all


def make_test_requiring_ndenumerate():
    pass


@pytest.mark.parametrize(
    "zonelist,error_type,error_message",
    [
        ([1], ValueError, "list must contain two or"),
        ((1,), ValueError, "tuple must be of length 2, was 1"),
        ({"a": 2}, TypeError, "zonelist must be either list"),
        (1, TypeError, "zonelist must be either list"),
        ("zonelist", TypeError, "zonelist must be either list"),
        ([1, 3], ValueError, "zonelist must be strictly increasing"),
        ([1, 2, 1], ValueError, "zonelist must be strictly increasing"),
    ],
)
def test_invalid_zonelist_type(tmp_path, zonelist, error_type, error_message):
    wellstring = """1.01
Unknown
name 0 0 0
1
Zonelog DISC 1 zone1 2 zone2
1 2 3 1
3 4 5 2
"""
    fpath = tmp_path / "well.rmswell"
    kwargs = {"zonelogname": "Zonelog"}
    well = string_to_well(fpath, wellstring, kwargs)
    with pytest.raises(error_type) as msg:
        well.get_zonation_points(use_undef=False, tops=True, zonelist=zonelist)
    assert error_message in str(msg.value)


def test_not_tops_points(tmp_path):
    wellstring = """1.01
Unknown
name 0 0 0
1
Zonelog DISC 1 zone1 2 zone2 3 zone3
1 2 3 1
4 5 6 1
7 8 9 2
10 11 12 2
13 14 15 3
"""
    fpath = tmp_path / "well.rmswell"
    kwargs = {"zonelogname": "Zonelog"}
    well = string_to_well(fpath, wellstring, kwargs)
    points = well.get_zonation_points(use_undef=False, tops=False, zonelist=[2, 3])
    assert len(points) == 2
    assert (points["X_UTME"] == [7.0, 14.0]).all
    assert (points["Y_UTMN"] == [8.0, 15.0]).all


def test_thickness_points():
    pass


def test_include_limit(tmp_path):
    wellstring = """1.01
Unknown
name 0 0 0
1
Zonelog DISC 1 zone1 2 zone2 3 zone3
1 2 3 1
4 5 6 1
7 8 9 2
10 11 12 2
13 14 15 3
"""
    fpath = tmp_path / "well.rmswell"
    kwargs = {"zonelogname": "Zonelog"}
    well = string_to_well(fpath, wellstring, kwargs)
    points = well.get_zonation_points(
        use_undef=False, tops=False, zonelist=[2, 3], incl_limit=12
    )
    assert len(points) == 2
    assert (points["X_UTME"] == [7.0, 14.0]).all
    assert (points["Y_UTMN"] == [8.0, 15.0]).all


def test_zonepoints_from_list(tmp_path):
    wellstring = """1.01
Unknown
name 0 0 0
1
Zonelog DISC 1 zone1 2 zone2 3 zone3
1 2 3 1
4 5 6 1
7 8 9 2
10 11 12 2
13 14 15 3
"""
    fpath = tmp_path / "well.rmswell"
    kwargs = {"zonelogname": "Zonelog"}
    well = string_to_well(fpath, wellstring, kwargs)
    points = well.get_zonation_points(use_undef=False, tops=True, zonelist=[2, 3])
    assert len(points) == 2
    assert (points["X_UTME"] == [7.0, 14.0]).all
    assert (points["Y_UTMN"] == [8.0, 15.0]).all


def test_zonepoints_from_tuple(tmp_path):
    wellstring = """1.01
Unknown
name 0 0 0
1
Zonelog DISC 1 zone1 2 zone2 3 zone3 4 zone4
1 2 3 1
4 5 6 1
7 8 9 2
10 11 12 2
13 14 15 3
16 17 18 4
"""
    fpath = tmp_path / "well.rmswell"
    kwargs = {"zonelogname": "Zonelog"}
    well = string_to_well(fpath, wellstring, kwargs)
    points = well.get_zonation_points(
        use_undef=False,
        tops=True,
        zonelist=(
            2,
            4,
        ),
    )
    assert len(points) == 2
    assert (points["X_UTME"] == [7.0, 14.0, 17.0]).all
    assert (points["Y_UTMN"] == [8.0, 15.0, 18.0]).all


def test_default_zonelist():
    pass
