from metrics import compute_metrics
from metrics.jetstream_metrics_dict import JETSTREAM_METRIC_DICT
import xarray as xr


def load_uv_data(data_path):
    """
        Make this more general and add and test the data_dir
    """
    data_dir = 'data/'
    UKESM1_SSP585_U = xr.open_dataset(data_dir + "ua_day_UKESM1-0-LL_ssp585_r2i1p1f2_gn_20150101-20491230.nc")
    UKESM1_SSP585_V = xr.open_dataset(data_dir + "va_day_UKESM1-0-LL_ssp585_r2i1p1f2_gn_20150101-20491230.nc")
    UKESM1_SSP585 = xr.merge([UKESM1_SSP585_U, UKESM1_SSP585_V])
    ukesm1_ssp585 = compute_metrics.MetricComputer(UKESM1_SSP585, all_metrics=JETSTREAM_METRIC_DICT)
    ukesm1_ssp585 = ukesm1_ssp585.sel(lat=slice(0, 90))
    return ukesm1_ssp585


def main(data_path, metrics=None, subset=False, subset_kwargs={}, **kwargs):
    print("Starting!")
    ukesm1_ssp585 = load_uv_data(data_path)
    
    if metrics is None:
        print('Warning: No metric given. Aborting process. Please use \'-m\' tag to declare metric name and see jetstream_metric_dict.py for a list of all metrics')
        return
    
    for metric in metrics:
        print("calculating metric: %s" % (metric))
        try:
            # TODO: move this try and catch to the actual method
            # TODO: is this necessary? return_coord_error = False
            if subset:
                print('Warning: User has chosen to not subset data. Watch RAM usuage!!')
                subset_kwargs = {"ignore_coords":["plev"]}
                # TODO: is this necessary? return_coord_error = True
            result = ukesm1_ssp585.compute_metric_from_data(metric, subset_kwargs=subset_kwargs)
            print('result:', result)
        except Exception as e:
            print("Unable to perform experiment. Error is:",e)
    print("done!")

