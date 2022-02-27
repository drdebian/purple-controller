"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.17.6
"""

from kedro.pipeline import Pipeline, node
from .nodes import get_ev_data, load_pv_data
from purple_controller.commons.nodes import load_lila_config


def create_pipeline(**kwargs):
    return Pipeline([
        node(
            func=load_lila_config,
            inputs=["raw_config_lila", "raw_config_cars"],
            outputs="config_model",
            name="load_lila_config_node",
        ),
        node(
            func=load_pv_data,
            inputs=["location_data", "params:timing", "config_model"],
            outputs="pv_data",
            name="load_pv_data_node",
        ),





    ])
