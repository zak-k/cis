"""Tests for ungridded_data module
"""
from unittest import TestCase, skipIf
from hamcrest import assert_that, is_, contains_inanyorder
from nose.tools import raises, assert_almost_equal
from cis.test.util.mock import make_regular_2d_ungridded_data, make_regular_2d_ungridded_data_with_missing_values, \
    make_regular_2d_with_time_ungridded_data

import numpy as np

from cis.data_io.Coord import CoordList, Coord
from cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData, Metadata, UngriddedDataList

try:
    import pandas
except ImportError:
    # Disable all these tests if pandas is not installed.
    pandas = None

skip_pandas = skipIf(pandas is None, 'Test(s) require "pandas", which is not available.')


class TestUngriddedData(TestCase):

    def test_can_create_ungridded_data(self):
        ug = make_regular_2d_ungridded_data()
        assert(ug.data.size == 15)

    def test_get_all_points_returns_points(self):
        ug = make_regular_2d_ungridded_data()
        points = ug.get_all_points()
        num_points = len([p for p in points])
        assert(num_points == 15)

    def test_get_non_masked_points_returns_points(self):
        ug = make_regular_2d_ungridded_data_with_missing_values()
        points = ug.get_non_masked_points()
        num_points = len([p for p in points])
        assert(num_points == 12)

    def test_get_coordinates_points_returns_points(self):
        ug = make_regular_2d_ungridded_data_with_missing_values()
        points = ug.get_coordinates_points()
        num_points = len([p for p in points])
        assert(num_points == 15)

    def test_can_add_history(self):
        ug = make_regular_2d_ungridded_data()

        new_history = 'This is a new history entry.'
        ug.add_history(new_history)
        assert(ug.metadata.history.find(new_history) >= 0)

    def test_GIVEN_numpy_array_data_with_missing_coordinate_values_WHEN_data_THEN_missing_values_removed(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        y = np.ma.masked_array(y, np.zeros(y.shape, dtype=bool))
        y.mask[1, 2] = True

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        coords = CoordList([x, y])

        data = np.reshape(np.arange(15) + 1.0, (5, 3))

        ug = UngriddedData(data, Metadata(), coords)
        data = ug.data.flatten()
        assert_that(len(data), is_(14))
        for coord in ug.coords():
            assert_that(len(coord.points), is_(14))

    @skip_pandas
    def test_GIVEN_ungridded_data_WHEN_call_as_data_frame_THEN_returns_valid_data_frame(self):
        from cis.test.util.mock import make_regular_4d_ungridded_data
        from datetime import datetime

        ug_data = make_regular_4d_ungridded_data()
        df = ug_data.as_data_frame()

        assert_that(df['rainfall_flux'][5] == 6)
        assert_that(df['latitude'][17] == 0)
        assert_that(df['latitude'].ix[datetime(1984,8,31)][0] == 10)
        assert_that(df['rainfall_flux'].median() == 25.5)

    @skip_pandas
    def test_GIVEN_ungridded_data_with_no_time_WHEN_call_as_data_frame_THEN_returns_valid_data_frame(self):
        from cis.test.util.mock import make_regular_2d_ungridded_data

        ug_data = make_regular_2d_ungridded_data()
        df = ug_data.as_data_frame()

        assert_that(df['rain'][5] == 6)
        assert_that(df['lat'][7] == 0)
        assert_that(df['rain'].median() == 8.0)

    @skip_pandas
    def test_GIVEN_ungridded_data_with_missing_vals_WHEN_call_as_data_frame_THEN_returns_valid_data_frame(self):
        from cis.test.util.mock import make_regular_2d_ungridded_data_with_missing_values

        ug_data = make_regular_2d_ungridded_data_with_missing_values()
        df = ug_data.as_data_frame()

        assert_that(df['rain'][5] == 6)
        assert_that(df['latitude'][7] == 0)
        assert_that(df['rain'].median() == 7.5)
        assert_that(np.isnan(df['rain'][8]))


class TestUngriddedDataLazyLoading(TestCase):

    def test_GIVEN_missing_coord_values_WHEN_data_THEN_missing_values_removed(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        y = np.ma.masked_array(y, np.zeros(y.shape, dtype=bool))
        y.mask[1, 2] = True

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        coords = CoordList([x, y])

        data = np.reshape(np.arange(15) + 1.0, (5, 3))

        ug = UngriddedData(None, Metadata(), coords, lambda x: data)
        data = ug.data.flatten()
        assert_that(len(data), is_(14))

    def test_GIVEN_missing_coord_values_WHEN_data_flattened_THEN_missing_values_removed(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        y = np.ma.masked_array(y, np.zeros(y.shape, dtype=bool))
        y.mask[1, 2] = True

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        coords = CoordList([x, y])

        data = np.reshape(np.arange(15) + 1.0, (5, 3))

        ug = UngriddedData(None, Metadata(), coords, lambda x: data)
        data = ug.data_flattened
        assert_that(len(data), is_(14))

    def test_GIVEN_missing_coord_values_WHEN_coords_points_THEN_missing_values_removed(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        y = np.ma.masked_array(y, np.zeros(y.shape, dtype=bool))
        y.mask[1, 2] = True

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        coords = CoordList([x, y])

        data = np.reshape(np.arange(15) + 1.0, (5, 3))

        ug = UngriddedData(None, Metadata(), coords, lambda x: data)
        coords = ug.coords()
        for coord in coords:
            assert_that(len(coord.points), is_(14))

    def test_GIVEN_missing_coord_values_WHEN_coords_data_THEN_missing_values_removed(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        y = np.ma.masked_array(y, np.zeros(y.shape, dtype=bool))
        y.mask[1, 2] = True

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        coords = CoordList([x, y])

        data = np.reshape(np.arange(15) + 1.0, (5, 3))

        ug = UngriddedData(None, Metadata(), coords, lambda x: data)
        coords = ug.coords()
        for coord in coords:
            assert_that(len(coord.data), is_(14))

    def test_GIVEN_missing_coord_values_WHEN_coords_flattened_THEN_missing_values_removed(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        y = np.ma.masked_array(y, np.zeros(y.shape, dtype=bool))
        y.mask[1, 2] = True

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))
        coords = CoordList([x, y])

        data = np.reshape(np.arange(15) + 1.0, (5, 3))

        ug = UngriddedData(None, Metadata(), coords, lambda x: data)
        coords = ug.coords_flattened
        for coord in coords:
            if coord is not None:
                assert_that(len(coord), is_(14))


class TestUngriddedCoordinates(TestCase):

    def setUp(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)

        self.x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        self.y = Coord(y, Metadata(standard_name='longitude', units='degrees'))

        coords = CoordList([self.x, self.y])
        self.ug = UngriddedCoordinates(coords)

    def test_can_create_ungridded_coordinates(self):
        standard_coords = self.ug.coords().find_standard_coords()
        assert(standard_coords == [self.x, self.y, None, None, None])

    def test_get_coordinates_points_returns_points(self):
        points = self.ug.get_coordinates_points()
        num_points = len([p for p in points])
        assert(num_points == 15)

    def test_GIVEN_missing_coord_values_WHEN_coords_THEN_missing_values_removed(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        y = np.ma.masked_array(y, np.zeros(y.shape, dtype=bool))
        y.mask[1, 2] = True

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))

        coords = CoordList([x, y])

        ug = UngriddedCoordinates(coords)
        coords = ug.coords()
        for coord in coords:
            assert_that(len(coord.data), is_(14))

    def test_GIVEN_missing_coord_values_WHEN_coords_flattened_THEN_missing_values_removed(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        y = np.ma.masked_array(y, np.zeros(y.shape, dtype=bool))
        y.mask[1, 2] = True

        x = Coord(x, Metadata(standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(standard_name='longitude', units='degrees'))

        coords = CoordList([x, y])

        ug = UngriddedCoordinates(coords)
        coords = ug.coords_flattened
        for coord in coords:
            if coord is not None:
                assert_that(len(coord), is_(14))

    @skip_pandas
    def test_GIVEN_ungridded_coords_WHEN_call_as_data_frame_THEN_returns_valid_data_frame(self):

        df = self.ug.as_data_frame()

        assert_that(df['latitude'][13] == 10)
        assert_that(df['longitude'][0] == -5)


    @skip_pandas
    def test_GIVEN_ungridded_coords_with_time_WHEN_call_as_data_frame_THEN_returns_valid_data_frame(self):
        from datetime import datetime
        ug = make_regular_2d_with_time_ungridded_data()
        ug_coords = UngriddedCoordinates(ug._coords)

        df = ug_coords.as_data_frame()

        assert_that(df['latitude'][13] == 10)
        assert_that(df['longitude'][0] == -5)
        assert_that(df['longitude'][datetime(1984,8,28)] == 0)


class TestUngriddedDataList(TestCase):

    def setUp(self):
        x_points = np.arange(-10, 11, 5)
        y_points = np.arange(-5, 6, 5)
        y, x = np.meshgrid(y_points, x_points)
        x = Coord(x, Metadata(name='lat', standard_name='latitude', units='degrees'))
        y = Coord(y, Metadata(name='lon', standard_name='longitude', units='degrees'))
        data = np.reshape(np.arange(15) + 1.0, (5, 3))
        self.coords = CoordList([x, y])

        ug1 = UngriddedData(data, Metadata(standard_name='rainfall_flux', long_name="TOTAL RAINFALL RATE: LS+CONV KG/M2/S",
                                           units="kg m-2 s-1", missing_value=-999), self.coords)
        ug2 = UngriddedData(data * 0.1, Metadata(standard_name='snowfall_flux', long_name="TOTAL SNOWFALL RATE: LS+CONV KG/M2/S",
                                                 units="kg m-2 s-1", missing_value=-999), self.coords)
        self.ungridded_data_list = UngriddedDataList([ug1, ug2])


    def test_GIVEN_data_containing_multiple_matching_coordinates_WHEN_coords_THEN_only_unique_coords_returned(self):

        unique_coords = self.ungridded_data_list.coords()
        assert_that(len(unique_coords), is_(2))
        assert_that(isinstance(unique_coords, CoordList))
        coord_names = [coord.standard_name for coord in unique_coords]
        assert_that(coord_names, contains_inanyorder('latitude', 'longitude'))

    @skip_pandas
    def test_GIVEN_multiple_ungridded_data_WHEN_call_as_data_frame_THEN_returns_valid_data_frame(self):

        df = self.ungridded_data_list.as_data_frame()

        assert_that(df['rainfall_flux'][5] == 6)
        assert_almost_equal(df['snowfall_flux'][5], 0.6)
        assert_that(df['lat'][13] == 10)
        assert_that(df['lon'][0] == -5)

    @skip_pandas
    def test_GIVEN_multiple_ungridded_data_with_missing_data_WHEN_call_as_data_frame_THEN_returns_valid_data_frame(self):
        d = np.reshape(np.arange(15) + 10.0, (5, 3))

        data = np.ma.masked_array(d, np.zeros(d.shape, dtype=bool))
        data.mask[1,2] = True

        ug3 = UngriddedData(data, Metadata(name='hail', long_name="TOTAL HAIL RATE: LS+CONV KG/M2/S",
                                           units="kg m-2 s-1", missing_value=-999), self.coords)

        self.ungridded_data_list.append(ug3)

        df = self.ungridded_data_list.as_data_frame()

        assert_that(df['rainfall_flux'][5] == 6)
        assert_almost_equal(df['snowfall_flux'][5], 0.6)
        assert_that(df['lat'][13] == 10)
        assert_that(df['lon'][0] == -5)
        assert_almost_equal(df['hail'][1], 11.0)
        assert_that(np.isnan(df['hail'][np.ravel_multi_index([1, 2], (5, 3))]))

        self.ungridded_data_list.pop()


@skip_pandas
class TestPandasHelperFunctions(TestCase):

    @raises(ValueError)
    def test_GIVEN_masked_array_WHEN_call_to_flat_ndarray_NO_copy_THEN_raises_ValueError(self):
        from cis.data_io.ungridded_data import _to_flat_ndarray
        d = np.reshape(np.arange(15) + 10.0, (5, 3))

        data = np.ma.masked_array(d, np.zeros(d.shape, dtype=bool))
        data.mask[2] = True

        _to_flat_ndarray(data, copy=False)

    def test_GIVEN_masked_array_WHEN_call_to_flat_ndarray_with_copy_THEN_returns_a_flat_copy(self):
        from cis.data_io.ungridded_data import _to_flat_ndarray
        d = np.reshape(np.arange(15) + 10.0, (5, 3))

        data = np.ma.masked_array(d, np.zeros(d.shape, dtype=bool))
        data.mask[2,2] = True

        new = _to_flat_ndarray(data, copy=True)

        assert_that(np.isnan(new[np.ravel_multi_index([2, 2], (5, 3))]))

if __name__ == '__main__':
    import nose
    nose.runmodule()
