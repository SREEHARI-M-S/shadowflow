from shadowflow.graph.change_detection import outputs_for_changed_sql
from shadowflow.models.pipeline import PipelineDefinition, SqlStep


def test_outputs_for_changed_sql_by_filename() -> None:
    definition = PipelineDefinition(
        name="demo",
        steps=[
            SqlStep(
                path="pipeline/01_clean_users.sql",
                sql="",
                inputs=["users"],
                outputs=["clean_users"],
            ),
            SqlStep(
                path="pipeline/02_enrich_users.sql",
                sql="",
                inputs=["clean_users"],
                outputs=["enriched_users"],
            ),
        ],
    )
    outputs = outputs_for_changed_sql(definition, {"01_clean_users.sql"})
    assert outputs == {"clean_users"}
