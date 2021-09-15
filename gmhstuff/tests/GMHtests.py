# GMHtests.py

from gmhstuff import GMHstuff as gmh
import pytest


# Sanity-checking:
def test_always_passes():
    assert True


# def test_always_fails():
#     assert False


# Now the REAL testing starts...

# Register marks:
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "sensor_info: Tests get_sensor_info() fn."
    )
    config.addinivalue_line(
        "markers", "rtncode: Tests rtncode_to_errmsg() fn."
    )
    config.addinivalue_line(
        "markers", "get_disp: Tests get_disp_unit() fn."
    )
    config.addinivalue_line(
        "markers", "get_range: Tests get_min_range() and get_max_range() fns."
    )
    config.addinivalue_line(
        "markers", "sw_info: Tests get_sw_info() fn."
    )
    config.addinivalue_line(
        "markers", "meas_attribs: Tests get_meas_attributes() fn."
    )
    config.addinivalue_line(
        "markers", "measure: Tests measure() fn."
    )
    config.addinivalue_line(
        "markers", "open_close: Tests open() and close() fns."
    )
    config.addinivalue_line(
        "markers", "transmit: Tests transmit() fn."
    )
    config.addinivalue_line(
        "markers", "get_xxx: Tests various get_...() fns."
    )

# Set up fixtures first...
@pytest.fixture
def demo_sensor():  # Test behaviour of GMH sensor in demo mode (COM0):
    return gmh.GMHSensor(0, demo=True)


@pytest.fixture
def probe_info(demo_sensor):
    return demo_sensor.get_sensor_info()


@pytest.fixture
def first_key(probe_info):
    return next(probe_info.keys().__iter__())


# get_sensor_info tests:
@pytest.mark.sensor_info
def test_get_sensor_info_rtn_dict(probe_info):
    """
    get_sensor_info() should return a dict.
    """
    assert isinstance(probe_info, dict)


@pytest.mark.sensor_info
def test_get_sensor_info_rtnkey0_str(first_key):
    """
    First key (in fact, ALL keys) in sensor_info dict
    should be a str.
    """
    assert isinstance(first_key, str)


@pytest.mark.sensor_info
def test_get_sensor_info_rtnval0_tuple(first_key, probe_info):
    """
    First value (in fact, ALL values) in sensor_info dict
    should be a tuple.
    """
    assert isinstance(probe_info[first_key], tuple)


@pytest.mark.sensor_info
def test_get_sensor_info_rtnval00_int(first_key, probe_info):
    """
    First element in first value in sensor_info dict
    should be int.
    """
    assert isinstance(probe_info[first_key][0], int)


@pytest.mark.sensor_info
def test_get_sensor_info_rtnval00_int(first_key, probe_info):
    """
    2nd element in first value in sensor_info dict
    should be a str.
    """
    assert isinstance(probe_info[first_key][1], str)


# rtncode_to_errmsg() tests:
@pytest.mark.rtncode
def test_rtncode_to_errmsg_no_stat_zero_in_rtn_str(demo_sensor):
    """
    A rtncode of 0 should return a str.
    """
    assert isinstance(demo_sensor.rtncode_to_errmsg(0), str)


# @pytest.mark.rtncode
# def test_rtncode_to_errmsg_stat_zero_in_rtn_tuple(demo_sensor):
#     """
#     ???
#     """
#     assert isinstance(demo_sensor.rtncode_to_errmsg(0, True), tuple)


# @pytest.mark.rtncode
# def test_rtncode_to_errmsg_stat_zero_in_rtn0_str(demo_sensor):
#     assert isinstance(demo_sensor.rtncode_to_errmsg(0, True)[0], str)


# @pytest.mark.rtncode
# def test_rtncode_to_errmsg_stat_zero_in_rtn1_str(demo_sensor):
#     assert isinstance(demo_sensor.rtncode_to_errmsg(0, True)[1], str)


# open_port() tests:
@pytest.mark.open_close
def test_open_port_rtn_int(demo_sensor):
    """
    open_port should return int.
    """
    assert isinstance(demo_sensor.open_port(), int)


# close() tests:
@pytest.mark.open_close
def test_close_rtn_int(demo_sensor):
    """
    close() should return int.
    """
    assert isinstance(demo_sensor.close(), int)


# transmit() tests:
@pytest.mark.transmit
def test_transmit_rtn_int(demo_sensor):
    """
    Sending 'GetStatus' to chan 1, using transmit(),
    should return an int.
    """
    assert isinstance(demo_sensor.transmit(1, 'GetStatus'), int)


# get_type() tests:
@pytest.mark.get_xxx
def test_get_type_rtn_str(demo_sensor):
    """
    get_type() should return a str.
    """
    assert isinstance(demo_sensor.get_type(), str)


# get_num_chans() tests:
@pytest.mark.get_xxx
def test_get_num_chans_rtn_int(demo_sensor):
    """
    get_num_chans() should return int.
    """
    assert isinstance(demo_sensor.get_num_chans(), int)


# get_status() tests:
@pytest.mark.get_xxx
def test_get_status_rtn_str(demo_sensor):
    """
    get_status() should return a str.
    """
    assert isinstance(demo_sensor.get_status(1), str)


# get_unit() tests:
@pytest.mark.get_xxx
def test_get_unit_rtn_str(demo_sensor):
    """
    get_unit() should return a str.
    """
    assert isinstance(demo_sensor.get_unit(1), str)


# get_disp_unit() tests:
@pytest.mark.get_disp
def test_get_disp_unit_rtn_str(demo_sensor):
    """
    get_disp_unit() should return a str.
    """
    assert isinstance(demo_sensor.get_disp_unit(1), str)


# get_disp_min_range tests:
@pytest.mark.get_disp
def test_get_disp_min_range_rtn_number(demo_sensor):
    """
    get_disp_min_range() should return a float or int.
    """
    assert isinstance(demo_sensor.get_disp_min_range(1), (int, float))


# get_disp_max_range tests:
@pytest.mark.get_disp
def test_get_disp_max_range_rtn_number(demo_sensor):
    """
    get_disp_max_range() should return a float or int.
    """
    assert isinstance(demo_sensor.get_disp_max_range(1), (int, float))


# get_min_range tests:
@pytest.mark.get_range
def test_get_min_range_rtn_number(demo_sensor):
    """
    get_min_range() should return a float or int.
    """
    assert isinstance(demo_sensor.get_min_range(1), (int, float))


# get_max_range tests:
@pytest.mark.get_range
def test_get_max_range_rtn_number(demo_sensor):
    """
    get_max_range() should return a float or int.
    """
    assert isinstance(demo_sensor.get_max_range(1), (int, float))


# get_power_off_time tests:
def test_get_power_off_time_rtn_number(demo_sensor):
    """
    get_power_off_time() should return a float or int.
    """
    assert isinstance(demo_sensor.get_power_off_time(), (int, float))


# get_sw_info tests:
@pytest.mark.sw_info
def test_get_sw_info_rtn_tuple(demo_sensor):
    """
    get_sw_info() should return a tuple.
    """
    assert isinstance(demo_sensor.get_sw_info(), tuple)


@pytest.mark.sw_info
def test_demo_get_sw_info_rtn0_float(demo_sensor):
    """
    First item in get_sw_info() returned tuple should be a float.
    """
    assert isinstance(demo_sensor.get_sw_info()[0], float)


@pytest.mark.sw_info
def test_demo_get_sw_info_rtn1_int(demo_sensor):
    """
    2nd item in get_sw_info() returned tuple should be int.
    """
    assert isinstance(demo_sensor.get_sw_info()[1], int)


# set_power_off_time (mins) tests:
@pytest.mark.power_off
@pytest.mark.parametrize('off_time,rtn', [
    (-1, -1),
    (0, 0),
    (1, 1),
    (60, 60)
])
def test_set_power_off_time_output_is_input(demo_sensor, off_time, rtn):
    """
    set_power_off_time() should always return -1 (for a demo sensor).
    """
    assert demo_sensor.set_power_off_time(off_time) == rtn


# get_meas_attributes tests:
@pytest.mark.meas_attribs
def test_get_meas_attributes_rtn_tuple(demo_sensor):
    """
    get_meas_attributes() should return a tuple.
    """
    assert isinstance(demo_sensor.get_meas_attributes('T'), tuple)


@pytest.mark.meas_attribs
def test_get_meas_attributes_rtn_val0_int(demo_sensor):
    """
    First item of get_meas_attributes() returned tuple should be int.
    """
    assert isinstance(demo_sensor.get_meas_attributes('T')[0], int)


@pytest.mark.meas_attribs
def test_get_meas_attributes_rtn_val1_str(demo_sensor):
    """
    2nd item of get_meas_attributes() returned tuple should be a str.
    """
    assert isinstance(demo_sensor.get_meas_attributes('T')[1], str)


# measure tests:
@pytest.mark.measure
def test_measure_rtn_tuple(demo_sensor):
    """
    measure() should return a tuple.
    """
    assert isinstance(demo_sensor.measure('T'), tuple)


@pytest.mark.measure
def test_measure_rtn_val0_float(demo_sensor):
    """
    First item of measure() tuple should be a float.
    """
    assert isinstance(demo_sensor.measure('T')[0], float)


@pytest.mark.measure
def test_measure_rtn_val1_str(demo_sensor):
    """
    2nd item of measure() tuple should be a str.
    """
    assert isinstance(demo_sensor.measure('T')[1], str)

