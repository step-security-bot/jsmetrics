# -*- coding: utf-8 -*-

"""
    Metrics used to identify or classify jet-stream in the literature

    All functions should return a xarray.Dataset unless otherwise stated
"""

# imports
import numpy as np
from . import jetstream_metrics_utils
from . import general_utils, windspeed_utils

# docs
__author__ = "Thomas Keel"
__email__ = "thomas.keel.18@ucl.ac.uk"
__status__ = "Development"


def koch_et_al_2006(data, ws_threshold=30):
    """
    TODO: check with chris
    TODO: add equation to this doc

    Returns
    ----------
    weighted_average_ws : DataArray
    """
    print("Step 1: Calculate weighted sum...")
    # Step 1.1: get all pressure levels in data as list and make sure hPa
    # TODO: what if mbar?
    all_plevs_hPa = general_utils.get_all_plev_hPa(data)
    # Step 1.2 get weighted sum windspeed
    sum_weighted_ws = jetstream_metrics_utils.get_sum_weighted_ws(
        data, all_plevs_hPa
    )
    # Step 2: calculate average weighted
    print("Step 2: Calculate weighted average...")
    weighted_average_ws = jetstream_metrics_utils.get_weighted_average_ws(
        sum_weighted_ws, all_plevs_hPa
    )
    # Step 3: apply threshold
    print("Step 3: Apply windspeed threshold of %s m/s..." % (ws_threshold))
    weighted_average_ws = weighted_average_ws.where(
        weighted_average_ws >= ws_threshold
    )
    weighted_average_ws = weighted_average_ws.fillna(0.0)
    # turn into dataset
    weighted_average_ws = weighted_average_ws.rename(
        "weighted_average_ws"
    ).to_dataset()
    return weighted_average_ws


def archer_caldeira_2008(data):
    """
    Will calculate only the mass-weighted wind speed
    Similar to Koch et al. 2006 -> "To overcome this problem,
        we define jet stream properties via integrated quantities,
        which are more numerically stable and less grid-dependent
        than are simple maxima and minima."
    """
    print("Step 1. Get monthly means")
    mon_mean = data.groupby("time.month").mean()
    print("Step 2. Calculate mass weighted average")
    mass_weighted_average = (
        jetstream_metrics_utils.get_mass_weighted_average_ws(mon_mean)
    )
    mass_flux_weighted_pressure = (
        jetstream_metrics_utils.calc_mass_flux_weighted_pressure(mon_mean)
    )
    mass_flux_weighted_latitude = (
        jetstream_metrics_utils.calc_mass_flux_weighted_latitude(
            mon_mean, lat_min=15, lat_max=75
        )
    )
    data = data.assign(
        {
            "mass_weighted_average_ws": (
                ("month", "lat", "lon"),
                mass_weighted_average.data,
            ),
            "mass_flux_weighted_pressure": (
                ("month", "lat", "lon"),
                mass_flux_weighted_pressure.data,
            ),
            "mass_flux_weighted_latitude": (
                ("month", "lon"),
                mass_flux_weighted_latitude.data,
            ),
        }
    )
    return data


def schiemann_et_al_2009(data):
    """
    Write function description
    """
    print("Step 1. Calculate wind vector")
    data["ws"] = windspeed_utils.get_resultant_wind(data["ua"], data["va"])
    print("Step 2. Calculate jet maximas")
    data = data.groupby("time").map(
        jetstream_metrics_utils.get_local_jet_maximas_by_day_by_plev
    )
    return data


def woolings_et_al_2010(data, filter_freq=10, window_size=61):
    """
    Follows an in-text description of 4-steps describing the algorithm of
    jet-stream identification from Woolings et al. (2010).
    Will calculate this metric based on data
    (regardless of pressure level of time span etc.).

    Parameters
    ----------
    data (xarray.Dataset): input data containing u and v wind
    filter_freq (int): number of days in filter
    window_size (int): number of days in window for Lancoz filter

    returns:
        max_lat_ws (numpy.ndarray):
    """
    # Step 1
    print("Step 1: calculating long and/or plev mean...")
    zonal_mean = jetstream_metrics_utils.get_zonal_mean(data)
    # Step 2
    print("Step 2: Applying %s day lancoz filter..." % (filter_freq))
    lancoz_filtered_mean_data = jetstream_metrics_utils.apply_lanczos_filter(
        zonal_mean["ua"], filter_freq, window_size
    )  # TODO make way of assuring that a dataarray is passed
    # Step 3
    print("Step 3: Calculating max windspeed and lat where max ws found...")
    max_lat_ws = np.array(
        list(
            map(
                jetstream_metrics_utils.get_latitude_and_speed_where_max_ws,
                lancoz_filtered_mean_data[:],
            )
        )
    )
    zonal_mean_lat_ws = jetstream_metrics_utils.assign_lat_and_ws_to_data(
        zonal_mean, max_lat_ws
    )
    # Step 4
    print("Step 4: Make climatology")
    climatology = general_utils.get_climatology(zonal_mean_lat_ws, "month")
    # Step 5
    print("Step 5: Apply low-freq fourier filter to both max lats and max ws")
    fourier_filtered_lats = (
        jetstream_metrics_utils.apply_low_freq_fourier_filter(
            climatology["max_lats"].values, highest_freq_to_keep=2
        )
    )
    fourier_filtered_ws = (
        jetstream_metrics_utils.apply_low_freq_fourier_filter(
            climatology["max_ws"].values, highest_freq_to_keep=2
        )
    )
    # Step 6
    print("Step 6: Join filtered climatology back to the data")
    time_dim = climatology["max_ws"].dims[0]
    fourier_filtered_data = (
        jetstream_metrics_utils.assign_filtered_lats_and_ws_to_data(
            zonal_mean_lat_ws,
            fourier_filtered_lats,
            fourier_filtered_ws,
            dim=time_dim,
        )
    )
    return fourier_filtered_data


def manney_et_al_2011(data, ws_core_threshold=40, ws_boundary_threshold=30):
    """
    Write function description

    Also see Manney et al. 2011, 2014, 2017 and 2018
    """
    print("Step 1. Run Jet-stream Core Idenfication Algorithm")
    data = data.groupby("time").map(
        jetstream_metrics_utils.run_jet_core_algorithm_on_one_day,
        (
            ws_core_threshold,
            ws_boundary_threshold,
        ),
    )
    return data


def penaortiz_et_al_2013(data):
    """
    Write function description

    TODO: maybe class
    """
    print("Step 1. Calculate wind vector")
    data["ws"] = windspeed_utils.get_resultant_wind(data["ua"], data["va"])
    print(
        "Step 2. Make array of zeros for local wind maxima location algorithm"
    )
    data = jetstream_metrics_utils.get_empty_local_wind_maxima_data(data)
    print("Step 3. Find local wind maxima locations by day")
    data = data.groupby("time").map(
        jetstream_metrics_utils.get_local_wind_maxima_by_day
    )
    print("Step 4. Get number of days per month with local wind maxima")
    data = jetstream_metrics_utils.get_number_of_days_per_monthyear_with_local_wind_maxima(
        data
    )
    print("TODO: Sort into PJ and STJ")
    return data


def screen_and_simmonds_2013(data):
    """
    Write function description
    Slightly adjusted in Screen and Simmonds 2014
    TODO: ask Chris about interpolation method
    TODO: insure that Earth sphericity is accounted for in the perimeter calc
    """
    return


def kuang_et_al_2014(data, occurence_ws_threshold=30):
    """
    Looks to get event-based jet occurrence percentage and jet center
    occurrence of (UT)JS. May take a long time for a lot of data
    TODO: ask chris to check
    """
    print(
        "Step 1. Run Jet-stream Occurence and Centre Algorithm \
                (1 for occurence, 2 for core)"
    )
    data = data.groupby("time").map(
        jetstream_metrics_utils.run_jet_occurence_and_centre_alg_on_one_day,
        (occurence_ws_threshold,),
    )
    return data


def francis_vavrus_2015(data):
    """
    Write function description
    MCI
    """
    print("Step 1. calculating Meridional Circulation Index from data")
    data["mci"] = jetstream_metrics_utils.calc_meridional_circulation_index(
        data
    )

    print("Step 2. TODO Calculate anomaly from season")
    # maybe TODO: Step ?? Calculate anomaly from season
    return data


def local_wave_activity(data):
    """
    Introduced by Huang and Nakamura for Potential Vorticity, but then used by:
    Martineau 2017, Chen 2015 and Blackport & Screen 2020 use LWA
    with 500 hPa zg instead of pv
    TODO: Ask Chris about equation in Blackport 2020 and others
    """
    return data


def cattiaux_et_al_2016(data):
    """
    Write function description
    """
    print("Step 1. get zonal average for each timestep")
    data["zonal_mean_zg_30Nto70N"] = (
        data["zg"].sel(lat=slice(30, 70)).groupby("time").mean(...)
    )
    print("Step 2. Get latitude circle of 50 N")
    circle_50N = jetstream_metrics_utils.get_latitude_circle_linestring(
        50, 0, 360
    )
    print("Step 3. Loop over each time step and calculate sinousity")
    data = data.groupby("time").map(
        lambda row: jetstream_metrics_utils.get_sinousity_of_zonal_mean_zg(
            row, circle_50N
        )
    )
    return data


def grise_polvani_2017(data):
    """
    Write function description
    See also Ceppi et al. 2012
    Works on Southern Hemisphere
    TODO: work out if relevant as this method also uses poleward edge of
    sub-tropical dry zone and poleward edge of Hadley cell
    derived from precip. record
    """
    # Step 1.
    print("Step 1. Calculate zonal-mean")
    zonal_mean = jetstream_metrics_utils.get_zonal_mean(data)
    print(
        "Step 2. Get the 3 latitudes and speeds around max zonal wind-speed\
                (e.g. lat-1, lat, lat+1)"
    )
    all_max_lats_and_ws = np.array(
        list(
            map(
                jetstream_metrics_utils.get_3_latitudes_and_speed_around_max_ws,
                zonal_mean["ua"],
            )
        )
    )
    print(
        "Step 3. Apply quadratic function to get max latitude\
                 at 0.01 degree resolution"
    )
    scaled_max_lats = []
    for max_lat_and_ws in all_max_lats_and_ws:
        scaled_max_lat = jetstream_metrics_utils.get_latitude_where_max_ws_at_reduced_resolution(
            max_lat_and_ws, resolution=0.01
        )
        scaled_max_lats.append(scaled_max_lat)
    print("Step 4. Assign scaled max lats back to data")
    data = data.assign({"max_lat_0.01": (("time"), scaled_max_lats)})
    return data


def molnos_et_al_2017(data):
    """
    Write function description
    """
    return data


def ceppi_et_al_2018(data):
    """
    Write function description
    TODO: what is meant by the centroid??
    "similar methods used in: Chen et al. 2008; Ceppi et al. 2014"

    Returns: centroid latitude of u-wind for one day
    """
    all_centroids = []
    if data["time"].count() > 1:
        for time_coord in data["time"]:
            sub_data = data.sel(time=time_coord)
            centroid_lat = jetstream_metrics_utils.get_centroid_jet_lat(
                sub_data
            )
            all_centroids.append(centroid_lat)
    else:
        centroid_lat = jetstream_metrics_utils.get_centroid_jet_lat(data)
        all_centroids.append(centroid_lat)
    data = data.assign({"jet_lat_centroid": (("time"), all_centroids)})
    return data


def kern_et_al_2018(data):
    """
    Write function description
    TODO: ask about equation
    """
    return data


def rikus_2018(data):
    """
    Write function description
    """
    return data


def simpson_et_al_2018(data):
    """
    Write function description
    TODO: ask about interpolation
    Before comparing the variability between the reanalyses and the models,
    each dataset is first interpolated onto a 2*2 longitude–latitude grid
    using a cubic spline interpolation and then isotropically smoothed
    in the spectral domain retaining only scales larger than total
    wavenumber 42 according to
    Sardeshmukh and Hoskins [1984, their Eq. (9) with n0=42 and r=1].
    """
    return data


def bracegirdle_et_al_2019(data):
    """
    Write function description
    TODO: work out if relevant
    TODO: check southern hemisphere works
    NOTE: for Southern Hemisphere
    """
    assert data["plev"].count() == 1, "data needs to have one 'plev' value"
    # Step 1
    print("Step 1. Make seasonal & annual climatologies")
    seasonal_climatology = general_utils.get_climatology(data, "season")
    annual_climatology = general_utils.get_climatology(data, "year")
    # Step 2
    print("Step 2. Get zonal mean from climatologies")
    seasonal_zonal_mean = seasonal_climatology.mean("lon")
    annual_zonal_mean = annual_climatology.mean("lon")
    # Step 3
    print(
        "Step 3. Cubic spline interpolation to each climatology\
         at latitude resolution of 0.075 degrees"
    )
    (
        seasonal_max_lats,
        seasonal_max_ws,
    ) = jetstream_metrics_utils.run_cubic_spline_interpolation_for_each_climatology_to_get_max_lat_and_ws(
        seasonal_zonal_mean, resolution=0.075, time_col="season"
    )
    (
        annual_max_lats,
        annual_max_ws,
    ) = jetstream_metrics_utils.run_cubic_spline_interpolation_for_each_climatology_to_get_max_lat_and_ws(
        annual_zonal_mean, resolution=0.075, time_col="year"
    )
    # Step 4
    print(
        "Step 4. Assign jet-stream position (JPOS) and\
                 jet-stream strength (JSTR) back to data"
    )
    data = data.assign(
        {
            "seasonal_JPOS": (("season"), seasonal_max_lats),
            "annual_JPOS": (("year"), annual_max_lats),
            "seasonal_JSTR": (("season"), seasonal_max_ws),
            "annual_JSTR": (("year"), annual_max_ws),
        }
    )
    return data


def lee_et_al_2019(data):
    """
    Write function description
    TODO: work out if relevant as wind shear of jet-stream rather than location
    variable used: temperature, u-wind, specific gas constant for dry air,
    the Coriolis parameter, pressure, northward distance.
    TODO: and add to dict if relevant
    """
    return data


def chemke_and_ming_2020(data):
    """
    Write function description
    TODO: ask about equation
    """
    return data