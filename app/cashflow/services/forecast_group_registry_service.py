from app.utils.paths import resource_path
import yaml


FORECAST_GROUPS_PATH = resource_path(
    "app/cashflow/config/forecast_groups.yaml"
)


def load_forecast_groups():

    path = FORECAST_GROUPS_PATH

    if not path.exists():

        return {}

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        data = yaml.safe_load(
            file
        )

    if not data:

        return {}

    return data.get(
        "forecast_groups",
        {}
    )


def resolve_forecast_group(
    entity_name: str,
):

    forecast_groups = (
        load_forecast_groups()
    )

    for (
        group_name,
        group_data,
    ) in (
        forecast_groups.items()
    ):

        entities = (
            group_data.get(
                "entities",
                []
            )
        )

        if entity_name in entities:

            return group_name

    return "Other"