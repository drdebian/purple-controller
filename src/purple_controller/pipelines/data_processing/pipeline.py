from kedro.pipeline import Pipeline, node

from .nodes import concatenate_partitions, load_lila_config, store_partition


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=concatenate_partitions,
                inputs="raw_lila",
                outputs="concatenated_lila",
                name="concatenate_lila_node",
            ),
            node(
                func=store_partition,
                inputs="concatenated_lila",
                outputs="table_lila",
                name="store_lila_node",
                confirms="raw_lila"
            ),
            node(
                func=concatenate_partitions,
                inputs="raw_auto1",
                outputs="concatenated_auto1",
                name="concatenate_auto1_node",
            ),
            node(
                func=store_partition,
                inputs="concatenated_auto1",
                outputs="table_auto1",
                name="store_auto1_node",
                confirms="raw_auto1"
            ),
            node(
                func=concatenate_partitions,
                inputs="raw_auto2",
                outputs="concatenated_auto2",
                name="concatenate_auto2_node",
            ),
            node(
                func=store_partition,
                inputs="concatenated_auto2",
                outputs="table_auto2",
                name="store_auto2_node",
                confirms="raw_auto2"
            ),
            node(
                func=concatenate_partitions,
                inputs="raw_auto3",
                outputs="concatenated_auto3",
                name="concatenate_auto3_node",
            ),
            node(
                func=store_partition,
                inputs="concatenated_auto3",
                outputs="table_auto3",
                name="store_auto3_node",
                confirms="raw_auto3"
            ),
            node(
                func=concatenate_partitions,
                inputs="raw_auto4",
                outputs="concatenated_auto4",
                name="concatenate_auto4_node",
            ),
            node(
                func=store_partition,
                inputs="concatenated_auto4",
                outputs="table_auto4",
                name="store_auto4_node",
                confirms="raw_auto4"
            ),
            node(
                func=load_lila_config,
                inputs=["raw_config_lila", "raw_config_cars"],
                outputs="config_model",
                name="load_lila_config_node",
            ),


        ]
    )
