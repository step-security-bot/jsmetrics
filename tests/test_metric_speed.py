from metrics import compute_metrics, data_formatter
from metrics.jetstream_metrics_dict import JETSTREAM_METRIC_DICT
import xarray as xr
import matplotlib.pyplot as plt


def main(data_path, **kwargs):
    print("Starting!")
    all_metrics = JETSTREAM_METRIC_DICT
    data_dir = 'data/'
    UKESM1_SSP585_U = xr.open_dataset(data_dir + "ua_day_UKESM1-0-LL_ssp585_r2i1p1f2_gn_20150101-20491230.nc")
    UKESM1_SSP585_V = xr.open_dataset(data_dir + "va_day_UKESM1-0-LL_ssp585_r2i1p1f2_gn_20150101-20491230.nc")
    UKESM1_SSP585 = xr.merge([UKESM1_SSP585_U, UKESM1_SSP585_V])
    ukesm1_ssp585 = data_formatter.DataFormatter(UKESM1_SSP585)
    ukesm1_ssp585 = ukesm1_ssp585.subset(lat=slice(0, 90))
    # ukesm1_ssp585.get_available_metrics(all_metrics, return_coord_error=True)
    
    one_metric = 'Woolings2010' # metric_to_use
    result = ukesm1_ssp585.compute_metric_from_data(one_metric, all_metrics=all_metrics, return_coord_error=False) # , subset_kwargs={'ignore_coords':['plev']
    del result
    # if result is not None:
    #     max_lats = result[:,0]
    #     max_ws = result[:,1]
    #     fig, ax = plt.subplots(1)
    #     ax.plot(max_lats)
    #     ax.plot(max_ws)
    #     plt.legend(['latitude of max windspeed', 'windspeed'])
    print("done!")
 