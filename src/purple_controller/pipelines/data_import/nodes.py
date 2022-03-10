import pandas as pd
from typing import Dict, Any, Callable, Tuple


def concatenate_partitions(partitions: Dict[str, Callable[[], Any]], model_timestamps: Dict[str, pd.Timestamp], mtd: pd.DataFrame) -> pd.DataFrame:
    """Concatenate partitions from an partitioned dataset into a single dataframe.

    Args:
        partitions (Dict[str, Callable]): Dictionary of dataframe loading functions to concatenate indexed by partition name

    Returns:
        pd.DataFrame: Dataframe containing concatenated dataframes
    """

    # print(model_timestamps['now'], model_timestamps['past_from'],
    #       model_timestamps['past_to'])

    result = pd.DataFrame()
    maxdatetime = pd.to_datetime(max(mtd.mtd))
    print("mtd: ", maxdatetime)

    for partition_key, partition_load_func in sorted(partitions.items()):

        # extract timestamp from partition name
        partition_date = partition_key.split("_")[-2]
        partition_time = partition_key.split("_")[-1]
        partition_datetime = pd.to_datetime(
            ' '.join([partition_date, partition_time]), format='%Y%m%d %H%M')

        # if partition_datetime >= model_timestamps['past_from'] and partition_datetime <= model_timestamps['now']:
        if partition_datetime > maxdatetime and partition_datetime <= model_timestamps['now']:
            partition_data = partition_load_func()
            result = pd.concat([result, partition_data], ignore_index=True, sort=False)
        # else:
        #     print("Ignoring partition: ", partition_key)

    print(result)

    return result


# pd.DataFrame:
def store_partition(partition: pd.DataFrame, mtd: pd.DataFrame) -> Tuple:
    """Passthrough function to store a concatenated dataframe partition

    Args:
        partition (pd.DataFrame): Dataframe containing concatenated partition dataframes

    Returns:
        pd.DataFrame: Dataframe ready for storage
        int: number of records in Dataframe
    """

    # maxdatetime = max(mtd.mtd)
    # # print("maxtimedate:", maxdatetime)
    # # print(partition.loc[partition.TimeDate > maxdatetime])

    # partition_delta = partition.loc[partition.TimeDate > maxdatetime].copy()

    # rowcount = len(partition_delta)

    # return partition_delta, rowcount

    rowcount = len(partition)

    return partition, rowcount
