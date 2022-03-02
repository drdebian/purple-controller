from kedro.pipeline import Pipeline, node

from .nodes import concatenate_partitions, store_partition


def create_pipeline(**kwargs):
    return Pipeline(
        [
            # node(
            #     func=load_lila_config,
            #     inputs=["raw_config_lila", "raw_config_cars"],
            #     outputs="config_model",
            #     name="load_lila_config_node",
            # ),
            node(
                func=concatenate_partitions,
                inputs="raw_location",
                outputs="concatenated_location",
                name="concatenate_location_node",
            ),
            node(
                func=store_partition,
                inputs="concatenated_location",
                outputs=["table_location", "rowcount_location"],
                name="store_location_node",
                confirms="raw_location"
            ),


            node(
                func=concatenate_partitions,
                inputs="raw_charger1",
                outputs="concatenated_charger1",
                name="concatenate_charger1_node",
            ),
            node(
                func=store_partition,
                inputs="concatenated_charger1",
                outputs=["table_charger1", "rowcount_charger1"],
                name="store_charger1_node",
                confirms="raw_charger1"
            ),

            node(
                func=concatenate_partitions,
                inputs="raw_charger2",
                outputs="concatenated_charger2",
                name="concatenate_charger2_node",
            ),
            node(
                func=store_partition,
                inputs="concatenated_charger2",
                outputs=["table_charger2", "rowcount_charger2"],
                name="store_charger2_node",
                confirms="raw_charger2"
            ),

            node(
                func=concatenate_partitions,
                inputs="raw_charger3",
                outputs="concatenated_charger3",
                name="concatenate_charger3_node",
            ),
            node(
                func=store_partition,
                # inputs="concatenated_charger3",
                inputs="concatenated_charger1",
                outputs=["table_charger3", "rowcount_charger3"],
                name="store_charger3_node",
                confirms="raw_charger3"
            ),

            node(
                func=concatenate_partitions,
                inputs="raw_charger4",
                outputs="concatenated_charger4",
                name="concatenate_charger4_node",
            ),
            node(
                func=store_partition,
                # inputs="concatenated_charger4",
                inputs="concatenated_charger1",
                outputs=["table_charger4", "rowcount_charger4"],
                name="store_charger4_node",
                confirms="raw_charger4"
            ),

            node(
                func=concatenate_partitions,
                inputs="raw_charger5",
                outputs="concatenated_charger5",
                name="concatenate_charger5_node",
            ),
            node(
                func=store_partition,
                # inputs="concatenated_charger5",
                inputs="concatenated_charger1",
                outputs=["table_charger5", "rowcount_charger5"],
                name="store_charger5_node",
                confirms="raw_charger5"
            ),


            node(
                func=concatenate_partitions,
                inputs="raw_charger6",
                outputs="concatenated_charger6",
                name="concatenate_charger6_node",
            ),
            node(
                func=store_partition,
                # inputs="concatenated_charger6",
                inputs="concatenated_charger1",
                outputs=["table_charger6", "rowcount_charger6"],
                name="store_charger6_node",
                confirms="raw_charger6"
            ),

            node(
                func=concatenate_partitions,
                inputs="raw_car1",
                outputs="concatenated_car1",
                name="concatenate_car1_node",
            ),
            node(
                func=store_partition,
                # inputs="concatenated_car1",
                inputs="concatenated_carsample1",
                outputs=["table_car1", "rowcount_car1"],
                name="store_car1_node",
                confirms="raw_car1"
            ),

            node(
                func=concatenate_partitions,
                inputs="raw_car2",
                outputs="concatenated_car2",
                name="concatenate_car2_node",
            ),
            node(
                func=store_partition,
                # inputs="concatenated_car2",
                inputs="concatenated_carsample1",
                outputs=["table_car2", "rowcount_car2"],
                name="store_car2_node",
                confirms="raw_car2"
            ),

            node(
                func=concatenate_partitions,
                inputs="raw_car3",
                outputs="concatenated_car3",
                name="concatenate_car3_node",
            ),
            node(
                func=store_partition,
                # inputs="concatenated_car3",
                inputs="concatenated_carsample1",
                outputs=["table_car3", "rowcount_car3"],
                name="store_car3_node",
                confirms="raw_car3"
            ),

            node(
                func=concatenate_partitions,
                inputs="raw_car4",
                outputs="concatenated_car4",
                name="concatenate_car4_node",
            ),
            node(
                func=store_partition,
                # inputs="concatenated_car4",
                inputs="concatenated_carsample1",
                outputs=["table_car4", "rowcount_car4"],
                name="store_car4_node",
                confirms="raw_car4"
            ),

            node(
                func=concatenate_partitions,
                inputs="raw_car5",
                outputs="concatenated_car5",
                name="concatenate_car5_node",
            ),
            node(
                func=store_partition,
                # inputs="concatenated_car5",
                inputs="concatenated_carsample1",
                outputs=["table_car5", "rowcount_car5"],
                name="store_car5_node",
                confirms="raw_car5"
            ),

            node(
                func=concatenate_partitions,
                inputs="raw_car6",
                outputs="concatenated_car6",
                name="concatenate_car6_node",
            ),
            node(
                func=store_partition,
                # inputs="concatenated_car6",
                inputs="concatenated_carsample1",
                outputs=["table_car6", "rowcount_car6"],
                name="store_car6_node",
                confirms="raw_car6"
            ),
            node(
                func=concatenate_partitions,
                inputs="raw_carsample1",
                outputs="concatenated_carsample1",
                name="concatenate_carsample1_node",
            ),
            node(
                func=store_partition,
                inputs="concatenated_carsample1",
                outputs=["table_carsample1", "rowcount_carsample1"],
                name="store_carsample1_node",
                confirms="raw_carsample1"
            ),
            node(
                func=concatenate_partitions,
                inputs="raw_carsample2",
                outputs="concatenated_carsample2",
                name="concatenate_carsample2_node",
            ),
            node(
                func=store_partition,
                # inputs="concatenated_carsample2",
                inputs="concatenated_carsample1",
                outputs=["table_carsample2", "rowcount_carsample2"],
                name="store_carsample2_node",
                confirms="raw_carsample2"
            ),





        ]
    )
