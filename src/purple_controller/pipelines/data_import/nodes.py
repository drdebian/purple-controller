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
    """

    return partition


# def latest_partition(partition: pd.DataFrame) -> pd.DataFrame:

#     lpartition = partition.copy()
#     lpartition = lpartition.sort_values(by=['TimeDate'], ascending=False).head(1)
#     print(lpartition)

#     return lpartition


# def get_ev_data(partition: pd.DataFrame, ev_data: pd.DataFrame) -> pd.DataFrame:

#     print(ev_data)

#     return ev_data
