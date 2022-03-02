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
