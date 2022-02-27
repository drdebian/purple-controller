"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.17.6
"""

import pandas as pd
from typing import Dict, Any, Callable, Tuple


def load_pv_data(raw_pv_data: pd.DataFrame, timing: Dict, constants: Dict) -> pd.DataFrame:

    freq = int(60*timing['M_DT'])

    my_pv = raw_pv_data.copy()
    my_pv.index = pd.to_datetime(my_pv.index)
    my_pv['PV_kW'] = my_pv['PV-W']/1000  # convert W to kW
    my_pv['BESS_kWh'] = my_pv['Kreisel-SOC']*constants['E_EL_CAP'] / \
        100  # convert BESS SOC percentage to kWh
    my_pv = my_pv[['PV_kW', 'BESS_kWh']]
    my_pv = my_pv.resample(str(freq)+'T').mean().pad()  # resample to hourly

    print(my_pv)
    return my_pv


def load_ev_data(ev_participant_ids: pd.DataFrame, raw_ev_data: Dict[str, Callable[[], Any]], evparams: Dict, timing: Dict) -> pd.DataFrame:

    my_vehicles = ev_participant_ids[0:evparams['num_vehicles']]
    freq = int(60*timing['M_DT'])

    appended_data = []
    for v in my_vehicles:
        my_vehicle = raw_ev_data[evparams["partition_prefix"] + v]()
        my_vehicle.drop(columns=['charging_bool'],
                        inplace=True)  # drop unneeded columns
        my_vehicle = my_vehicle.resample(str(freq)+'T').agg(
            {'driving_bool': 'max', 'power_kW': 'mean', 'loadable_bool': 'min'}).pad().round(2)  # resample to hourly
        oldindex = my_vehicle.index
        # remove original index
        my_vehicle.reset_index(inplace=True, drop=True)
        newindex = pd.MultiIndex.from_tuples(
            list(zip([v]*len(oldindex), oldindex)), names=['vehicle', 'timestamp'])
        # set new index of vehicle and period
        my_vehicle = my_vehicle.set_index(newindex)
        appended_data.append(my_vehicle)
    my_ev = pd.concat(appended_data, axis=0)
    my_ev.rename(columns={"driving_bool": "driving", "power_kW": "power",
                          "loadable_bool": "loadable"}, inplace=True)
    return my_ev


def get_ev_data(ev_data: pd.DataFrame, ev_config: Dict) -> pd.DataFrame:

    print(ev_data)
    print(ev_config)

    return ev_data
