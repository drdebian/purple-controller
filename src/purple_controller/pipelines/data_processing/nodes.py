import pandas as pd
from typing import Dict, Any, Callable, Tuple


def concatenate_partitions(partitions: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Concatenate partitions from an incremental dataset into a single dataframe.

    Args:
        partitions (Dict[str, pd.DataFrame]): Dictionary of dataframes to concatenate indexed by partition name

    Returns:
        pd.DataFrame: Dataframe containing concatenated dataframes
    """

    result = pd.DataFrame()

    for partition_key, partition_data in sorted(partitions.items()):

        print(partition_key)
        result = pd.concat([result, partition_data], ignore_index=True, sort=False)

    print(result)

    return result


def store_partition(partition: pd.DataFrame) -> pd.DataFrame:
    """Passthrough function to store a concatenated dataframe partition

    Args:
        partition (pd.DataFrame): Dataframe containing concatenated partition dataframes

    Returns:
        pd.DataFrame: Dataframe ready for storage
        pd.DataFrame: Most current record of partition
    """

    return partition


def latest_partition(partition: pd.DataFrame) -> pd.DataFrame:

    lpartition = partition.copy()
    lpartition = lpartition.sort_values(by=['TimeDate'], ascending=False).head(1)
    print(lpartition)

    return lpartition


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
