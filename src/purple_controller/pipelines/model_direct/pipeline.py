"""
This is a boilerplate pipeline 'model_direct'
generated using Kedro 0.17.6
"""

from kedro.pipeline import Pipeline, node
from purple_controller.commons.nodes import (extract_model_solution_dataframes, get_current_ev_data, get_current_pv_data, get_ev_charge_limits, get_history_ev_data, get_history_pv_data, get_model_ev_data,
                                             get_model_pv_data, get_model_soc_inits, get_model_timestamps, plot_sys_timeseries_simple, predict_ev_data, predict_pv_data, solve_model)
from .nodes import construct_model_direct


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(func=get_model_timestamps,
                 inputs="params:timing",
                 outputs="model_timestamps",
                 name="get_model_timestamps_node",
                 ),
            # node(func=get_current_pv_data,
            #      inputs=["processed_pv_data", "model_timestamps"],
            #      outputs="current_pv_data",
            #      name="get_current_pv_data_node",
            #      ),
            # node(func=get_current_ev_data,
            #      inputs=["processed_ev_data", "model_timestamps"],
            #      outputs="current_ev_data",
            #      name="get_current_ev_data_node",
            #      ),
            # node(func=get_history_pv_data,
            #      inputs=["processed_pv_data", "model_timestamps"],
            #      outputs="history_pv_data",
            #      name="get_history_pv_data_node",
            #      ),
            # node(func=get_history_ev_data,
            #      inputs=["processed_ev_data", "model_timestamps"],
            #      outputs="history_ev_data",
            #      name="get_history_ev_data_node",
            #      ),
            # node(func=predict_pv_data,
            #      inputs=["history_pv_data", "params:timing"],
            #      outputs="predicted_pv_data",
            #      name="get_predicted_pv_data_node",
            #      ),
            # node(func=predict_ev_data,
            #      inputs=["history_ev_data", "params:timing"],
            #      outputs="predicted_ev_data",
            #      name="get_predicted_ev_data_node",
            #      ),
            # node(func=get_model_pv_data,
            #      inputs=["current_pv_data", "predicted_pv_data"],
            #      outputs="model_pv_data",
            #      name="get_model_pv_data_node",
            #      ),
            # node(func=get_model_ev_data,
            #      inputs=["current_ev_data", "predicted_ev_data"],
            #      outputs="model_ev_data",
            #      name="get_model_ev_data_node",
            #      ),
            # node(func=get_model_soc_inits,
            #      inputs=["params:constants", "model_ev_data"],
            #      outputs="model_soc_inits",
            #      name="get_model_soc_inits_node",
            #      ),
            # node(func=construct_model_direct,
            #      inputs=["params:timing", "params:constants",
            #              "model_pv_data", "model_ev_data", "model_soc_inits"],
            #      outputs="unsolved_direct_model",
            #      name="construct_direct_model_node",
            #      ),
            # node(func=solve_model,
            #      inputs=["unsolved_direct_model", "params:solverparams"],
            #      outputs="solved_direct_model",
            #      name="solve_direct_model_node",
            #      ),
            # node(func=extract_model_solution_dataframes,
            #      inputs="solved_direct_model",
            #      outputs="direct_solution_dictionary",
            #      name="extract_direct_solution_node",
            #      ),
            # node(func=plot_sys_timeseries_simple,
            #      inputs=["direct_solution_dictionary",
            #              "model_pv_data", "model_ev_data"],
            #      outputs="direct_solution_plot",
            #      name="plot_direct_solution_node",
            #      ),
            # node(func=get_ev_charge_limits,
            #      inputs="direct_solution_dictionary",
            #      outputs="ev_charge_limits",
            #      name="get_ev_charge_limits_node",
            #      ),

        ])
