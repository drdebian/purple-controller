"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.17.6
"""

import pandas as pd
from typing import Dict, Any, Callable, Tuple


def load_lila_config(config_lila: Dict, config_cars: Dict) -> Dict:
    """Function to parse original system configuration files into format suitable for use in a model

    Args:
        config_lila (Dict): Nested dictionary containing LiLa configuration parameters
        config_cars (Dict): Nested dictionary containing car configuration parameters

    Returns:
        Dict: Flattened dictionary containing consolidated configuration for use in model
    """

    model_config = {}

    model_config['E_EL_CAP'] = config_lila['LiLa']['battery']['capacity']
    model_config['P_EL_MAX'] = config_lila['LiLa']['battery']['maxChargingPower']
    model_config['P_EL_MIN'] = config_lila['LiLa']['battery']['maxDischargePower']
    model_config['P_PV_CAP'] = config_lila['LiLa']['pv']['maxPower']
    model_config['P_PV_ETA'] = .6

    model_config['P_CS_MAX'] = {}
    for cs in config_lila['LiLa']['chargingstations']:
        station = 'charger' + str(cs['stationId'])
        model_config['P_CS_MAX'][station] = cs['maxChargingPower']

    model_config['E_EV_CAP'] = {}
    model_config['P_EV_MAX'] = {}
    model_config['P_EV_MIN'] = {}
    model_config['vehicles'] = []
    for car in config_cars['cars']:
        vehicle = 'car'+str(car['carID'])
        if car['capacity']:
            model_config['E_EV_CAP'][vehicle] = car['capacity']
            model_config['P_EV_MAX'][vehicle] = car['maxChargingPower']
            model_config['P_EV_MIN'][vehicle] = car['minChargingPower']
            model_config['vehicles'].append(vehicle)

    print(model_config)

    return model_config


def get_ev_data(ev_data: pd.DataFrame, ev_config: Dict) -> pd.DataFrame:

    print(ev_data)
    print(ev_config)

    return ev_data
