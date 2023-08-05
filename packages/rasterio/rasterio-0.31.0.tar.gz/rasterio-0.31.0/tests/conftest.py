import functools
import operator
import os
import shutil
import sys

from click.testing import CliRunner
import py
import pytest
import numpy


DEFAULT_SHAPE = (10, 10)


if sys.version_info > (3,):
    reduce = functools.reduce

test_files = [os.path.join(os.path.dirname(__file__), p) for p in [
    'data/RGB.byte.tif', 'data/float.tif', 'data/float_nan.tif', 'data/shade.tif']]


def pytest_cmdline_main(config):
    # Bail if the test raster data is not present. Test data is not 
    # distributed with sdists since 0.12.
    if reduce(operator.and_, map(os.path.exists, test_files)):
        print("Test data present.")
    else:
        print("Test data not present. See download directions in tests/data/README.rst")
        sys.exit(1)


@pytest.fixture(scope='function')
def runner():
    return CliRunner()


@pytest.fixture(scope='function')
def data():
    """A temporary directory containing a copy of the files in data."""
    tmpdir = py.test.ensuretemp('tests/data')
    for filename in test_files:
        shutil.copy(filename, str(tmpdir))
    return tmpdir


@pytest.fixture
def basic_geometry():
    """
    Returns
    -------

    dict: GeoJSON-style geometry object.
        Coordinates are in grid coordinates (Affine.identity()).
    """

    return {
        'type': 'Polygon',
        'coordinates': [[(2, 2), (2, 4.25), (4.25, 4.25), (4.25, 2), (2, 2)]]
    }


@pytest.fixture
def basic_feature(basic_geometry):
    """
    Returns
    -------

    dict: GeoJSON object.
        Coordinates are in grid coordinates (Affine.identity()).
    """

    return {
        'geometry': basic_geometry,
        'properties': {
            'val': 15
        },
        'type': 'Feature'
    }


@pytest.fixture
def basic_featurecollection(basic_feature):
    """
    Returns
    -------

    dict: GeoJSON FeatureCollection object.
        Coordinates are in grid coordinates (Affine.identity()).
    """

    return {
        'features': [basic_feature],
        'type': 'FeatureCollection'
    }


@pytest.fixture
def basic_image():
    """
    A basic 10x10 array for testing sieve and shapes functions.
    Contains a square feature 3x3 (size 9).
    Equivalent to results of rasterizing basic_geometry with all_touched=True.

    Returns
    -------

    numpy ndarray
    """

    image = numpy.zeros(DEFAULT_SHAPE, dtype=numpy.uint8)
    image[2:5, 2:5] = 1

    return image


@pytest.fixture
def basic_image_2x2():
    """
    A basic 10x10 array for testing sieve and shapes functions.
    Contains a square feature 2x2 (size 4).
    Equivalent to results of rasterizing basic_geometry with all_touched=False.

    Returns
    -------

    numpy ndarray
    """

    image = numpy.zeros(DEFAULT_SHAPE, dtype=numpy.uint8)
    image[2:4, 2:4] = 1

    return image


@pytest.fixture
def pixelated_image(basic_image):
    """
    A basic 10x10 array for testing sieve functions.  Contains a square feature
    3x3 (size 9), with 2 isolated pixels.

    Returns
    -------

    numpy ndarray
    """

    image = basic_image.copy()
    image [0, 0] = 1
    image [8, 8] = 1

    return image


@pytest.fixture
def diagonal_image():
    """
    A 10x10 array for testing sieve functions, with only one diagonal filled.

    Returns
    -------

    numpy ndarray
    """

    image = numpy.zeros(DEFAULT_SHAPE, dtype=numpy.uint8)
    numpy.fill_diagonal(image, 1)
    return image


@pytest.fixture()
def pixelated_image_file(tmpdir, pixelated_image):
    """
    A basic raster file with a 10x10 array for testing sieve functions.
    Contains data from pixelated_image.

    Returns
    -------

    string
        Filename of test raster file
    """

    from affine import Affine
    import rasterio

    image = pixelated_image

    outfilename = str(tmpdir.join('pixelated_image.tif'))
    kwargs = {
        "crs": {'init': 'epsg:4326'},
        "transform": Affine.identity(),
        "count": 1,
        "dtype": rasterio.uint8,
        "driver": "GTiff",
        "width": image.shape[1],
        "height": image.shape[0],
        "nodata": 255
    }
    with rasterio.drivers():
        with rasterio.open(outfilename, 'w', **kwargs) as out:
            out.write_band(1, image)

    return outfilename
