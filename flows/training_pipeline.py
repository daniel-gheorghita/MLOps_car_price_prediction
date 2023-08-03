#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import os
import glob
from matplotlib import pyplot as plt
import numpy as np
from time import sleep, time
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
)
import mlflow
from mlflow import MlflowClient
from mlflow.entities import ViewType
import mlflow.sklearn
from pprint import pprint
from prefect import flow, task


AVAILABLE_DATA_PATH = "./data/available"
MODEL_NAME = "car-price-predictor"
DEBUG = False


# Connect to the MLFlow tracking server
mlflow.set_tracking_uri("http://0.0.0.0:5000")


@task()
def load_existing_dataset(input_folder):
    assert os.path.exists(
        input_folder
    ), f"Input location {input_folder} does not exist."
    files_list = glob.glob(os.path.join(input_folder, "*.csv"))
    print(f"Found {len(files_list)} data files.")
    if len(files_list) == 0:
        print("No data available.")
        return None
    df = pd.concat(map(pd.read_csv, files_list))
    print("Loaded available data.")
    return df


@task()
def train_model(df, feature_columns, target_column, model_type="LinearRegressor"):
    df = df.dropna().reset_index(drop=True)
    X = df[feature_columns].values
    # print(np.shape(X))
    y = df[target_column].values
    # print(np.shape(y))

    with mlflow.start_run():
        mlflow.log_param("model_type", model_type)
        mlflow.log_param("latest_data_year", df["year"].max())
        mlflow.log_param("feature_columns", feature_columns)
        mlflow.log_param("target_column", target_column)

        if model_type == "LinearRegressor":
            model = LinearRegression().fit(X, y)
        elif model_type == "GradientBoostingRegressor":
            model = GradientBoostingRegressor().fit(X, y)
        elif model_type == "RandomForestRegressor":
            model = RandomForestRegressor().fit(X, y)

        y_pred = model.predict(X)
        rmse = mean_squared_error(y, y_pred, squared=False)
        score = model.score(X, y)

        mlflow.log_metric("train_rmse", rmse)
        mlflow.log_metric("train_score", score)
        mlflow.sklearn.log_model(model, "model")

    return model


@task()
def evaluate_model(model, df_test, feature_columns, target_column, display=True):
    df_test = df_test.dropna().reset_index(drop=True)
    X = df_test[feature_columns].values
    y = df_test[target_column].values
    print("Model score :", model.score(X, y))
    y_pred = model.predict(X)
    rmse = mean_squared_error(y, y_pred, squared=False)
    print("Model rmse: ", rmse)
    if display:
        plt.plot(
            model.predict(df_test[feature_columns].values), label="Predicted", alpha=0.5
        )
        plt.plot(df_test[target_column].values, label="Measured", alpha=0.5)
        plt.legend()
        plt.show()

    return rmse


@task()
def compare_datasets(
    df, latest_training_data, feature_columns, target_column, display=True
):
    reference_data = df[df["year"] <= latest_training_data]
    current_data = df[df["year"] > latest_training_data]

    reference_data_mean_values = np.array(
        reference_data[feature_columns + [target_column]].mean().values
    )
    current_data_new_mean_values = np.array(
        current_data[feature_columns + [target_column]].mean().values
    )
    if display:
        plt.plot(
            current_data_new_mean_values / reference_data_mean_values * 100,
            label="new/available data [%]",
        )
        plt.xticks(
            list(range(len(reference_data_mean_values))),
            reference_data[feature_columns + [target_column]].mean().index,
            rotation=45,
        )
        plt.legend()
        plt.show()


@task()
def calculate_monitoring_metrics(
    model,
    df,
    latest_training_data,
    numerical_features=None,
    categorical_features=None,
    target_column=None,
):
    print(latest_training_data)
    print(df["year"].min(), df["year"].max())
    all_features_list = []
    if numerical_features:
        all_features_list = all_features_list + numerical_features
    if categorical_features:
        all_features = all_features_list + categorical_features

    column_mapping = ColumnMapping(
        prediction="prediction",
        numerical_features=numerical_features,
        categorical_features=categorical_features,
        target=target_column,
    )
    report = Report(
        metrics=[
            ColumnDriftMetric(column_name="prediction"),
            DatasetDriftMetric(),
            DatasetMissingValuesMetric(),
        ]
    )

    reference_data = df[df["year"] <= latest_training_data]
    current_data = df[df["year"] > latest_training_data]
    current_data["prediction"] = model.predict(
        current_data[all_features_list].fillna(0)
    )
    reference_data["prediction"] = model.predict(
        reference_data[all_features_list].fillna(0)
    )

    report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping,
    )

    result = report.as_dict()

    prediction_drift = result["metrics"][0]["result"]["drift_score"]
    num_drifted_columns = result["metrics"][1]["result"]["number_of_drifted_columns"]
    share_missing_values = result["metrics"][2]["result"]["current"][
        "share_of_missing_values"
    ]

    print("prediction_drift:", prediction_drift)
    print("num_drifted_columns:", num_drifted_columns)
    print("share_missing_values:", share_missing_values)

    return prediction_drift, num_drifted_columns, share_missing_values


@flow()
def main_training_flow(available_data_path, model_name, display=True):
    feature_cols = [
        "horsepower",
        "places",
        "doors",
        "speed",
        "consumption",
        "acceleration",
    ]
    # feature_cols = ['horsepower']
    target_col = "price_eur"
    latest_training_data = 1900
    latest_available_data = 1900
    model = None
    client = MlflowClient()
    if DEBUG:
        # Delete a registered model along with all its versions
        try:
            client.delete_registered_model(name=model_name)
        except:
            print(f"Model {MODEL_NAME} not present in the registry.")

    model = None
    print("----- Iteration -----")

    # Load data
    df = load_existing_dataset(available_data_path)
    if df is None:
        print("No available data for training.")
        return
    latest_available_data = df["year"].max()

    # Get the latest model version from the registry
    for rm in client.search_registered_models():
        if rm.latest_versions[0].name != model_name:
            continue
        run_id = rm.latest_versions[0].run_id
        run_obj = mlflow.get_run(run_id)
        run_metrics = run_obj.data.metrics
        run_params = run_obj.data.params
        latest_training_data = int(run_params["latest_data_year"])
        print(run_params)

        # Load the model
        model_uri = "runs:/{}/model".format(run_id)
        try:
            model = mlflow.sklearn.load_model(model_uri)
        except:
            print("No model found.")
    """
    model_version = "latest"
    try:
        model = mlflow.sklearn.load_model(model_uri=f"models:/{model_name}/{model_version}")
    except:
        print(f"Model {model_name}:{model_version} was not found.")
    """
    # if df is not None:
    #    model = train_model(df, feature_columns=feature_cols, target_column=target_col)
    #    latest_training_data = df['year'].max()

    # Monitoring
    if latest_training_data < latest_available_data:
        compare_datasets(
            df, latest_training_data, feature_cols, target_col, display=display
        )
        if model is not None:
            (
                prediction_drift,
                num_drifted_columns,
                share_missing_values,
            ) = calculate_monitoring_metrics(
                model, df.copy(), latest_training_data, numerical_features=feature_cols
            )
            rmse = evaluate_model(
                model,
                df[df["year"] > latest_training_data],
                feature_columns=feature_cols,
                target_column=target_col,
                display=display,
            )

    # Train model if it does not exist OR
    # Retrain if the performance dropped/there is drift in the new dataset
    if model is None or rmse > 1000 or num_drifted_columns > 1:
        EXPERIMENT_NAME = f"car-price-{int(time())}"
        mlflow.set_experiment(EXPERIMENT_NAME)
        for model_type in [
            "LinearRegressor",
            "GradientBoostingRegressor",
            "RandomForestRegressor",
        ]:
            model = train_model(
                df,
                feature_columns=feature_cols,
                target_column=target_col,
                model_type=model_type,
            )
            evaluate_model(
                model,
                df,
                feature_columns=feature_cols,
                target_column=target_col,
                display=display,
            )

        # Select the model with the lowest test RMSE
        experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
        best_run = client.search_runs(
            experiment_ids=experiment.experiment_id,
            filter_string="",
            run_view_type=ViewType.ACTIVE_ONLY,
            max_results=1,
            order_by=["metrics.train_rmse ASC"],
        )[0]
        # print(best_run)

        # Register the best model

        result = mlflow.register_model(
            f"runs:/{best_run.info.run_id}/model", model_name
        )


# In[14]:

if __name__ == "__main__":
    main_training_flow(
        available_data_path=AVAILABLE_DATA_PATH, model_name=MODEL_NAME, display=False
    )


# In[ ]:


# Test service
