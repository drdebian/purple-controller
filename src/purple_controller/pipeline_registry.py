"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline

from purple_controller.pipelines import data_import as di
from purple_controller.pipelines import data_processing as dp


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    #data_import_pipeline = di.create_pipeline()
    data_processing_pipeline = dp.create_pipeline()

    return {
        "__default__": data_processing_pipeline,
        # "di": data_import_pipeline,
        "dp": data_processing_pipeline,

    }
