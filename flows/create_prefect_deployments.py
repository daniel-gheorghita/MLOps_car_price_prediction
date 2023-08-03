from training_pipeline import main_training_flow, MODEL_NAME
from ETL_pipeline import main_data_flow, AVAILABLE_DATA_PATH, EXTERNAL_DATA_PATH

from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule

deployment_prices_data = Deployment.build_from_flow(
    flow=main_data_flow,
    name="Car price data pipeline deployment",
    schedule=(IntervalSchedule(interval=60)),
    parameters={
        "available_data_path": AVAILABLE_DATA_PATH,
        "external_data_path": EXTERNAL_DATA_PATH,
    },
    tags=["update"],
)

deployment_prices_models = Deployment.build_from_flow(
    flow=main_training_flow,
    name="Car price model training pipeline deployment",
    schedule=(IntervalSchedule(interval=48)),
    parameters={"available_data_path": AVAILABLE_DATA_PATH, "model_name": MODEL_NAME},
    tags=["train"],
)

if __name__ == "__main__":
    deployment_prices_data.apply()
    deployment_prices_models.apply()
