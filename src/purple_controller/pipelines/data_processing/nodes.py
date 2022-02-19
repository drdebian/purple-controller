import pandas as pd
from typing import Dict, Any, Callable


def concatenate_partitions(partitions: Dict[str, pd.DataFrame]) -> pd.DataFrame:

    result = pd.DataFrame()

    for partition_key, partition_data in sorted(partitions.items()):

        print(partition_key)
        result = pd.concat([result, partition_data], ignore_index=True, sort=False)
        #result = partition_data

    print(result)

    return result

    # return lilamain


def store_partition(partition: pd.DataFrame) -> pd.DataFrame:

    return partition


def load_lila_config(config_lila: Dict, config_cars: Dict) -> Dict:

    model_config = {}

    model_config['E_EL_CAP'] = config_lila['LiLa']['battery']['capacity']
    model_config['P_EL_MAX'] = config_lila['LiLa']['battery']['maxChargingPower']
    model_config['P_EL_MIN'] = config_lila['LiLa']['battery']['maxDischargePower']
    model_config['P_PV_CAP'] = config_lila['LiLa']['pv']['maxPower']
    model_config['P_PV_ETA'] = .6

    model_config['P_CS_MAX'] = {}
    for cs in config_lila['LiLa']['chargingstations']:
        station = 'station' + str(cs['stationId'])
        model_config['P_CS_MAX'][station] = cs['maxChargingPower']

    model_config['E_EV_CAP'] = {}
    model_config['P_EV_MAX'] = {}
    model_config['P_EV_MIN'] = {}
    model_config['vehicles'] = []
    for car in config_cars['cars']:
        vehicle = 'auto'+str(car['carID'])
        if car['capacity']:
            model_config['E_EV_CAP'][vehicle] = car['capacity']
            model_config['P_EV_MAX'][vehicle] = car['maxChargingPower']
            model_config['P_EV_MIN'][vehicle] = car['minChargingPower']
            model_config['vehicles'].append(vehicle)

    print(model_config)

    return model_config
