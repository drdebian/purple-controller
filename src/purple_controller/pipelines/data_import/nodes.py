import pandas as pd
from typing import Dict, Any, Callable, Tuple


def concatenate_partitions(partitions: Dict[str, Callable[[], Any]], model_timestamps: Dict[str, pd.Timestamp]) -> pd.DataFrame:
    """Concatenate partitions from an incremental dataset into a single dataframe.

    Args:
        partitions (Dict[str, pd.DataFrame]): Dictionary of dataframes to concatenate indexed by partition name

    Returns:
        pd.DataFrame: Dataframe containing concatenated dataframes
    """

    print(model_timestamps['now'], model_timestamps['past_from'],
          model_timestamps['past_to'])

    result = pd.DataFrame()

    for partition_key, partition_load_func in sorted(partitions.items()):

        # extract timestamp from partition name
        partition_date = partition_key.split("_")[-2]
        partition_time = partition_key.split("_")[-1]
        partition_datetime = pd.to_datetime(
            ' '.join([partition_date, partition_time]), format='%Y%m%d %H%M')

        if partition_datetime >= model_timestamps['past_from'] and partition_datetime <= model_timestamps['now']:
            partition_data = partition_load_func()
            result = pd.concat([result, partition_data], ignore_index=True, sort=False)
        # else:
        #     print("Ignoring partition: ", partition_key)

    print(result)

    return result


def store_partition(partition: pd.DataFrame) -> Tuple:  # pd.DataFrame:
    """Passthrough function to store a concatenated dataframe partition

    Args:
        partition (pd.DataFrame): Dataframe containing concatenated partition dataframes

    Returns:
        pd.DataFrame: Dataframe ready for storage
        int: number of records in Dataframe
    """

    rowcount = len(partition)

    return partition, rowcount
