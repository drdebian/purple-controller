"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.17.6
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Callable, Tuple


def depend_on_imported_data(**kwargs) -> Any:
    """dummy function to ensure data import is complete before database queries

    Returns:
        Any: _description_
    """
    result = 0
    for name, data in kwargs.items():
        result += 1

    return result


def load_pv_data(data_ready: Any, raw_pv_data: pd.DataFrame, timing: Dict, constants: Dict) -> pd.DataFrame:

    freq = int(60*timing['M_DT'])

    my_pv = raw_pv_data.copy()
    my_pv.index = pd.to_datetime(my_pv.index)
    my_pv['PV_kW'] = my_pv['PV-W']/1000  # convert W to kW
    my_pv['BESS_kWh'] = my_pv['Kreisel-SOC']*constants['E_EL_CAP'] / \
        100  # convert BESS SOC percentage to kWh
    my_pv = my_pv[['PV_kW', 'BESS_kWh', 'cntMeasurements']]
    my_pv = my_pv.resample(str(freq)+'T').mean().pad()  # resample to hourly

    print(my_pv)
    return my_pv


def load_ev_data(data_ready: Any, raw_ev_data: pd.DataFrame, config_model: Dict, timing: Dict, location: Dict) -> pd.DataFrame:

    my_vehicles = config_model['vehicles']
    freq = int(60*timing['M_DT'])
    numcolumns = ['']

    appended_data = []
    for v in my_vehicles:
        my_vehicle = raw_ev_data.copy().loc[pd.IndexSlice[v, :], :]

        my_vehicle.status = my_vehicle.status.fillna('idle')

        # my_vehicle['status'] = 'ride'

        my_vehicle.reset_index(inplace=True, drop=False)
        my_vehicle.timestamp = pd.to_datetime(my_vehicle.timestamp)
        my_vehicle.set_index('timestamp', inplace=True)
        my_vehicle = my_vehicle.resample(str(freq)+'T').agg(
            {'vehicle': 'max',
             'id': 'max',
             'status': 'max',
             'positionLat': 'mean',
             'positionLon': 'mean',
             'distanceLastCharge': 'mean',
             'avgSpeedLastCharge': 'mean',
             'stateOfCharge': 'mean',
             'cntMeasurements': 'mean',
             'chgSOC': 'mean',
             }
        ).pad()  # .round(2)  # resample
        my_vehicle['id'] = my_vehicle['id'].astype(int)

        my_vehicle['SOC_kWh'] = my_vehicle['stateOfCharge'] * \
            config_model['E_EV_CAP'][v]/100

        my_vehicle['power'] = np.maximum(-my_vehicle['chgSOC'], 0) * \
            config_model['E_EV_CAP'][v]/100

        my_vehicle.reset_index(inplace=True, drop=False)
        my_vehicle.set_index(['vehicle', 'timestamp'], inplace=True)

        my_vehicle['driving'] = False
        my_vehicle.loc[(my_vehicle['status'] == 'ride') | (
            my_vehicle['power'] > 0), 'driving'] = True

        my_vehicle['loadable'] = False
        my_vehicle.loc[(my_vehicle['status'] != 'ride') &
                       (round(my_vehicle['positionLat'], 3) == round(location['lat'], 3)) &
                       (round(my_vehicle['positionLon'], 3) == round(location['lon'], 3)) &
                       (my_vehicle['power'] <= 0), 'loadable'] = True

        appended_data.append(my_vehicle)
    my_ev = pd.concat(appended_data, axis=0)

    print(my_ev)

    return my_ev


# def get_ev_data(ev_data: pd.DataFrame, ev_config: Dict) -> pd.DataFrame:

#     print(ev_data)
#     print(ev_config)

#     return ev_data
