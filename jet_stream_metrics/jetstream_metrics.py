# -*- coding: utf-8 -*-

"""
    Metrics used to identify or classify jet-stream in the literature
"""

### imports
import numpy as np
import xarray as xr
from .import jetstream_metrics_utils
# import jetstream_metrics.jetstream_metrics_utils

### docs
__author__ = "Thomas Keel"
__email__ = "thomas.keel.18@ucl.ac.uk"
__status__ = "Development"


def woolings_et_al_2010(data, filter_freq=10, lat_min=15, lat_max=75):
    """
        Write function description
        TODO: maybe default values for freq and lat/lon bands
        TODO: add a useful exception capture
        TODO: maybe note about using season or not
    """
    # i.e. will calculate woolings metric based on data (regardless of pressure level of time span etc.)
    mean_data = data.mean(['lon','plev'])
    mean_data = mean_data.sel(lat=slice(lat_min, lat_max))
    lanczos_weights = jetstream_metrics_utils.low_pass_weights(61, 1/10)
    lanczos_weights_arr = xr.DataArray(lanczos_weights, dims=['window'])
    window_cons = mean_data['ua'].rolling(time=len(lanczos_weights_arr), center=True).construct('window').dot(lanczos_weights_arr)
    max_lat_ws = np.array(list(map(jetstream_metrics_utils.get_latitude_and_speed_where_max_ws, window_cons[:])))
    return max_lat_ws
    

def Koch_et_al_2006(data):
    """
        Write function description
    """
    # i.e. will calculate metric based on data (regardless of pressure level of time span etc.)
    return


def Ceppi_et_al_2015(data):
    """
        Write function description
    """
    # i.e. will calculate metric based on data (regardless of pressure level of time span etc.)
    return


def Ceppi_et_al_2015(data):
    """
        Write function description
    """
    # i.e. will calculate metric based on data (regardless of pressure level of time span etc.)
    return


def Ceppi_et_al_2015(data):
    """
        Write function description
    """
    # i.e. will calculate metric based on data (regardless of pressure level of time span etc.)
    return


def Ceppi_et_al_2015(data):
    """
        Write function description
    """
    # i.e. will calculate metric based on data (regardless of pressure level of time span etc.)
    return


def Ceppi_et_al_2015(data):
    """
        Write function description
    """
    # i.e. will calculate metric based on data (regardless of pressure level of time span etc.)
    return


def Ceppi_et_al_2015(data):
    """
        Write function description
    """
    # i.e. will calculate metric based on data (regardless of pressure level of time span etc.)
    return
