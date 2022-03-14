"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline

from purple_controller.pipelines import data_import as di
from purple_controller.pipelines import data_processing as dp
from purple_controller.pipelines import model_direct as md
from purple_controller.pipelines import model_rule as mr


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    data_import_pipeline = di.create_pipeline()
    data_processing_pipeline = dp.create_pipeline()
    model_direct_pipeline = md.create_pipeline()
    model_rule_pipeline = mr.create_pipeline()

    return {
        "__default__": model_rule_pipeline
        + data_import_pipeline
        + data_processing_pipeline,
        "data_import": data_import_pipeline,
        "data_processing": data_processing_pipeline,
        "model_direct": model_direct_pipeline + data_import_pipeline
        + data_processing_pipeline,
        "model_rule": model_rule_pipeline + data_import_pipeline
        + data_processing_pipeline,

    }
