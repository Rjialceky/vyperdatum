import os
from pytest import approx

from vyperdatum.core import *
from vyperdatum.vdatum_validation import vdatum_answers

gvc = VyperCore()
data_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
vdatum_answer = vdatum_answers[gvc.vdatum.vdatum_version]


def test_core_setup():
    # these tests assume you have the vdatum path setup in VyperCore
    # first time, you need to run it with the path to the vdatum folder, vc = VyperCore('path\to\vdatum')
    vc = VyperCore()
    assert os.path.exists(vc.vdatum.vdatum_path)
    assert vc.vdatum.grid_files
    assert vc.vdatum.polygon_files
    assert vc.vdatum.vdatum_version
    assert vc.vdatum.regions


def test_regions():
    vc = VyperCore()
    vc.set_input_datum((6318, 'mllw'))
    vc.set_region_by_bounds(-75.79179, 35.80674, -75.3853, 36.01585)
    assert len(vc.regions) == 2
    assert vc.regions[0].find('NCcoast') != -1
    assert vc.regions[1].find('NCinner') != -1


def test_3d_to_compound():
    vc = VyperCore()
    vc.set_input_datum((6319, 'mllw'))
    vc.set_region_by_bounds(-75.79179, 35.80674, -75.3853, 36.01585)
    assert len(vc.regions) == 2
    assert vc.regions[0].find('NCcoast') != -1
    assert vc.regions[1].find('NCinner') != -1


def test_out_of_bounds():
    vc = VyperCore()
    vc.set_input_datum((6318, 'mllw'))
    vc.set_region_by_bounds(-155.29119, 57.12611, -154.56609, 57.67068)
    assert vc.regions == []


def test_set_input_datum():
    vc = VyperCore()
    vc.set_input_datum(6318)
    vc.set_region_by_bounds(-75.79179, 35.80674, -75.3853, 36.01585)
    vc.set_input_datum('mllw')

    assert vc.in_crs.vyperdatum_str == 'mllw'
    assert vc.in_crs.pipeline_string == '[+proj=pipeline +step +proj=vgridshift grids=core\\geoid12b\\g2012bu0.gtx ' \
                                        '+step +inv +proj=vgridshift grids=NCcoast11_8301\\tss.gtx ' \
                                        '+step +proj=vgridshift grids=NCcoast11_8301\\mllw.gtx;' \
                                        '+proj=pipeline +step +proj=vgridshift grids=core\\geoid12b\\g2012bu0.gtx ' \
                                        '+step +inv +proj=vgridshift grids=NCinner11_8301\\tss.gtx ' \
                                        '+step +proj=vgridshift grids=NCinner11_8301\\mllw.gtx]'

    assert len(vc.regions) == 2
    assert vc.regions[0].find('NCcoast') != -1
    assert vc.regions[1].find('NCinner') != -1


def test_set_output_datum():
    vc = VyperCore()
    vc.set_input_datum(6318)
    vc.set_region_by_bounds(-75.79179, 35.80674, -75.3853, 36.01585)
    vc.set_output_datum('geoid')

    assert vc.out_crs.vyperdatum_str == 'geoid'
    assert vc.out_crs.pipeline_string == '[+proj=pipeline +step +proj=vgridshift grids=core\\geoid12b\\g2012bu0.gtx;+proj=pipeline +step +proj=vgridshift grids=core\\geoid12b\\g2012bu0.gtx]'
    assert len(vc.regions) == 2
    assert vc.regions[0].find('NCcoast') != -1
    assert vc.regions[1].find('NCinner') != -1


def _transform_region_dataset(region: str):
    vc = VyperCore()
    vc.set_input_datum(6318)
    vc.set_input_datum('ellipse')
    vc.set_output_datum((6318, 'geoid'))
    x = vdatum_answer[region]['x']
    y = vdatum_answer[region]['y']
    z = vdatum_answer[region]['z_nad83']
    newx, newy, newz, _, _ = vc.transform_dataset(x, y, z, include_vdatum_uncertainty=False)

    assert newx == approx(x, abs=0.0001)
    assert newy == approx(y, abs=0.0001)
    assert newz == approx(vdatum_answer[region]['z_navd88'], abs=0.002)

    vc = VyperCore()
    vc.set_input_datum(6318)
    vc.set_input_datum('ellipse')
    vc.set_output_datum((6318, 'mllw'))
    x = vdatum_answer[region]['x']
    y = vdatum_answer[region]['y']
    z = vdatum_answer[region]['z_nad83']
    newx, newy, newz, _, _ = vc.transform_dataset(x, y, z, include_vdatum_uncertainty=False)

    assert newx == approx(x, abs=0.0001)
    assert newy == approx(y, abs=0.0001)
    assert newz == approx(vdatum_answer[region]['z_mllw'], abs=0.002)

    vc = VyperCore()
    vc.set_input_datum(6318)
    vc.set_input_datum('ellipse')
    vc.set_output_datum((6318, 'mhw'))
    x = vdatum_answer[region]['x']
    y = vdatum_answer[region]['y']
    z = vdatum_answer[region]['z_nad83']
    newx, newy, newz, _, _ = vc.transform_dataset(x, y, z, include_vdatum_uncertainty=False)

    assert newx == approx(x, abs=0.0001)
    assert newy == approx(y, abs=0.0001)
    assert newz == approx(vdatum_answer[region]['z_mhw'], abs=0.002)


def _transform_region_stateplane_dataset(region: str):
    vc = VyperCore()
    vc.set_input_datum(6318)
    vc.set_input_datum('ellipse')
    vc.set_output_datum((vdatum_answer[region]['x_stateplane'][0], 'mllw'))
    x = vdatum_answer[region]['x']
    y = vdatum_answer[region]['y']
    z = vdatum_answer[region]['z_nad83']
    newx, newy, newz, _, _ = vc.transform_dataset(x, y, z, include_vdatum_uncertainty=False)

    assert newx == approx(vdatum_answer[region]['x_stateplane'][1], abs=0.1)
    assert newy == approx(vdatum_answer[region]['y_stateplane'][1], abs=0.1)
    assert newz == approx(vdatum_answer[region]['z_mllw'], abs=0.002)

    vc = VyperCore()
    vc.set_input_datum(6318)
    vc.set_input_datum('ellipse')
    vc.set_output_datum((vdatum_answer[region]['x_stateplane'][0], 'mhw'))
    x = vdatum_answer[region]['x']
    y = vdatum_answer[region]['y']
    z = vdatum_answer[region]['z_nad83']
    newx, newy, newz, _, _ = vc.transform_dataset(x, y, z, include_vdatum_uncertainty=False)

    assert newx == approx(vdatum_answer[region]['x_stateplane'][1], abs=0.1)
    assert newy == approx(vdatum_answer[region]['y_stateplane'][1], abs=0.1)
    assert newz == approx(vdatum_answer[region]['z_mhw'], abs=0.002)


def _transform_region_utm_dataset(region: str):
    vc = VyperCore()
    vc.set_input_datum(6318)
    vc.set_input_datum('ellipse')
    vc.set_output_datum((vdatum_answer[region]['x_utm'][0], 'mllw'))
    x = vdatum_answer[region]['x']
    y = vdatum_answer[region]['y']
    z = vdatum_answer[region]['z_nad83']
    newx, newy, newz, _, _ = vc.transform_dataset(x, y, z, include_vdatum_uncertainty=False)

    assert newx == approx(vdatum_answer[region]['x_utm'][1], abs=0.1)
    assert newy == approx(vdatum_answer[region]['y_utm'][1], abs=0.1)
    assert newz == approx(vdatum_answer[region]['z_mllw'], abs=0.002)

    vc = VyperCore()
    vc.set_input_datum(6318)
    vc.set_input_datum('ellipse')
    vc.set_output_datum((vdatum_answer[region]['x_utm'][0], 'mhw'))
    x = vdatum_answer[region]['x']
    y = vdatum_answer[region]['y']
    z = vdatum_answer[region]['z_nad83']
    newx, newy, newz, _, _ = vc.transform_dataset(x, y, z, include_vdatum_uncertainty=False)

    assert newx == approx(vdatum_answer[region]['x_utm'][1], abs=0.1)
    assert newy == approx(vdatum_answer[region]['y_utm'][1], abs=0.1)
    assert newz == approx(vdatum_answer[region]['z_mhw'], abs=0.002)


def _transform_dataset_inv(region: str):
    vc = VyperCore()
    vc.set_input_datum(vdatum_answer[region]['horiz_epsg'])
    vc.set_input_datum('mllw')
    vc.set_output_datum(6318)
    vc.set_output_datum('ellipse')
    x = vdatum_answer[region]['x']
    y = vdatum_answer[region]['y']
    z = vdatum_answer[region]['z_mllw']
    newx, newy, newz, _, _ = vc.transform_dataset(x, y, z, include_vdatum_uncertainty=False)

    assert newx == approx(newx, abs=0.0001)
    assert newy == approx(newy, abs=0.0001)
    assert newz == approx(vdatum_answer[region]['z_nad83'], abs=0.002)


def _transform_dataset_unc(region: str):
    vc = VyperCore()
    vc.set_input_datum(6318)
    vc.set_input_datum('ellipse')
    vc.set_output_datum('mllw')
    x = vdatum_answer[region]['x']
    y = vdatum_answer[region]['y']
    z = vdatum_answer[region]['z_nad83']
    newx, newy, newz, newunc, _ = vc.transform_dataset(x, y, z)

    assert newunc == approx(vdatum_answer[region]['z_mllw_unc'], abs=0.002)


def test_transform_north_carolina_dataset():
    _transform_region_dataset('north_carolina')


def test_transform_texas_dataset():
    _transform_region_dataset('texas')


def test_transform_california_dataset():
    _transform_region_dataset('california')


def test_transform_alaska_southeast_dataset():
    _transform_region_dataset('alaska_southeast')


def test_transform_north_carolina_stateplane_dataset():
    _transform_region_stateplane_dataset('north_carolina')


def test_transform_texas_stateplane_dataset():
    _transform_region_stateplane_dataset('texas')


def test_transform_california_stateplane_dataset():
    _transform_region_stateplane_dataset('california')


def test_transform_alaska_southeast_stateplane_dataset():
    _transform_region_stateplane_dataset('alaska_southeast')


def test_transform_north_carolina_utm_dataset():
    _transform_region_utm_dataset('north_carolina')


def test_transform_texas_utm_dataset():
    _transform_region_utm_dataset('texas')


def test_transform_california_utm_dataset():
    _transform_region_utm_dataset('california')


def test_transform_alaska_southeast_utm_dataset():
    _transform_region_utm_dataset('alaska_southeast')


def test_transform_north_carolina_inv_dataset():
    _transform_dataset_inv('north_carolina')


def test_transform_texas_inv_dataset():
    _transform_dataset_inv('texas')


def test_transform_california_inv_dataset():
    _transform_dataset_inv('california')


def test_transform_alaska_southeast_inv_dataset():
    _transform_dataset_inv('alaska_southeast')


def test_transform_north_carolina_unc_dataset():
    _transform_dataset_unc('north_carolina')


def test_transform_texas_unc_dataset():
    _transform_dataset_unc('texas')


def test_transform_california_unc_dataset():
    _transform_dataset_unc('california')


def test_transform_alaska_southeast_unc_dataset():
    _transform_dataset_unc('alaska_southeast')


def test_transform_dataset_multiple_regions():
    vc = VyperCore()
    vc.set_input_datum((6318, 'ellipse'))
    vc.set_output_datum('mllw')
    x = np.concatenate([vdatum_answer['texas']['x'], vdatum_answer['california']['x']])
    y = np.concatenate([vdatum_answer['texas']['y'], vdatum_answer['california']['y']])
    z = np.concatenate([vdatum_answer['texas']['z_nad83'], vdatum_answer['california']['z_nad83']])
    newx, newy, newz, newunc, newregion = vc.transform_dataset(x, y, z, include_vdatum_uncertainty=True, include_region_index=True)

    assert newx == approx(x, abs=0.0001)
    assert newy == approx(y, abs=0.0001)
    assert newz == approx(np.concatenate([vdatum_answer['texas']['z_mllw'], vdatum_answer['california']['z_mllw']]), abs=0.002)
    assert newunc == approx(np.concatenate([vdatum_answer['texas']['z_mllw_unc'], vdatum_answer['california']['z_mllw_unc']]), abs=0.002)
    assert np.unique(newregion).size == 2  # should only be two regions used
    assert newregion[0] == newregion[1] == newregion[2]
    assert newregion[3] == newregion[4] == newregion[5]


def test_transform_dataset_with_log():
    logfile = os.path.join(data_folder, 'newlog.txt')
    vc = VyperCore(logfile=logfile)
    vc.set_input_datum(6318)
    vc.set_input_datum('ellipse')
    vc.set_output_datum((6318, 'geoid'))
    x = vdatum_answer['texas']['x']
    y = vdatum_answer['texas']['y']
    z = vdatum_answer['texas']['z_nad83']
    newx, newy, newz, _, _ = vc.transform_dataset(x, y, z, include_vdatum_uncertainty=False)

    assert os.path.exists(logfile)
    vc.close()
    os.remove(logfile)
    assert not os.path.exists(logfile)
