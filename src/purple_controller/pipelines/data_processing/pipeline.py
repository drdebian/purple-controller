"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.17.6
"""

from kedro.pipeline import Pipeline, node
from .nodes import depend_on_imported_data, load_ev_data, load_pv_data
from purple_controller.commons.nodes import load_lila_config


def create_pipeline(**kwargs):
    return Pipeline([
        node(
            func=load_lila_config,
            inputs=["raw_config_lila", "raw_config_cars", "params:constants"],
            outputs="config_model",
            name="load_lila_config_node",
        ),
        node(
            func=load_pv_data,
            inputs=["data_ready", "location_data", "params:timing", "config_model"],
            outputs="processed_pv_data",
            name="load_pv_data_node",
        ),
        node(
            func=load_ev_data,
            inputs=["data_ready", "ev_data", "config_model",
                    "params:timing", "params:location"],
            outputs="processed_ev_data",
            name="load_ev_data_node",
        ),

        node(
            func=depend_on_imported_data,
            inputs={"rowcount_location": "rowcount_location",
                    "rowcount_car1": "rowcount_car1",
                    "rowcount_car2": "rowcount_car2",
                    "rowcount_car3": "rowcount_car3",
                    "rowcount_car4": "rowcount_car4",
                    "rowcount_car5": "rowcount_car5",
                    "rowcount_car6": "rowcount_car6",
                    "rowcount_charger1": "rowcount_charger1",
                    "rowcount_charger2": "rowcount_charger2",
                    "rowcount_charger3": "rowcount_charger3",
                    "rowcount_charger4": "rowcount_charger4",
                    "rowcount_charger5": "rowcount_charger5",
                    "rowcount_charger6": "rowcount_charger6",
                    },
            outputs="data_ready",
            name="depend_on_imported_data_node",
        ),



    ])
