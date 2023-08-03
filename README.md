# Car price prediction: MLOps pipeline

This is the final project for the MLOps Zoomcamp course by DataTalksClub.
The course material can be found on [Youtube](https://www.youtube.com/playlist?list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK) and on [Github](https://github.com/DataTalksClub/mlops-zoomcamp).
This project aims at implementing an automated pipeline with the following features:
* update the local dataset from a remote source (Pandas);
* train and retrain a prediction model (Sklearn);
* keep record of the models via experiment tracking (MLFlow);
* monitor the data and the model performance (Evidently);
* orchestrate and schedule the functional workflow (Prefect);
* containerize the environment and dependencies (Conda and Docker);
* apply quality checks (Pytest and black);
* orchestrate the non-functional workflow (Make).

The project's focus is on the MLOps practices and minimum time has been spent on the actual model training parts. 

## Dataset
The project uses the [European car prices dataset](https://sites.google.com/site/frankverbo/data-and-software/data-set-on-the-european-car-market?authuser=0) by [Frank Verboven](https://sites.google.com/site/frankverbo) from K.U. Leuven (Belgium).

This dataset has been selected for 3 main reasons:
* it has a rich and well-defined structure with multiple options for selecting model features;
* it is almost guaranteed to drift over time (prices due to inflation, car properties due to trends and technological advances);
* it is not the most popular dataset (sorry :D ).

## Background
The pipeline current uses a local "out-dated" dataset. Meaning that the data update is simulated. There are multiple files which contain yearly data in the **data/yearly** folder. The data update pipeline simply copies periodically one of these files into the **data/available** folder (this folder needs to be cleaned, otherwise it will no longer be updated when all the yearly data is copied). This is the folder that the training pipeline is using. If the current model has been trained on older data, it is expected that it's performance drops. Therefore, the training of a model happens if at least of the 3 conditions is met:
* there is no model in the model registry;
* the latest model in the registry shows a large RMSE on new data;
* the new data has columns with drift compared to the dataset used for training of the current model.

In order to actually use this pipeline with real online datasets, one would need to adapt the code in **flows/ETL_pipeline.py** to handle the new data source. 

The code in **flows/create_prefect_deployments.py** handles (as its name suggests) the creation of deployments using the Prefect framework. Modify this file to change the frequency of dataset update or model retraining. **Improvement point**: the model retraining could be triggered by the data update. Currently, these 2 pipelines are not synchronized.


## Deployment guide
The application is containerized with Docker, therefore Docker Engine needs to be installed. 
Clone this repository:
```
git clone https://github.com/daniel-gheorghita/MLOps_car_price_prediction.git
```
Navigate to the source folder:
```
cd mlops_car_price_prediction
```
On a MacOS or Linux-based machine, you can simply run the  script:
```
./start_service.sh
```
Connect to the container (if needed) by running the  script:
```
./connect_to_docker.sh
```
To turn off the service, simply run:
```
./stop_service.sh
```
If any of these scripts cannot be executed, please run:
```
chmod +x <script_name>
```
Service monitoring:
* orchestration and scheduling: [Prefect Dashboard](http://0.0.0.0:4200/dashboard);
* experiments tracking: [MLFlow Experiments](http://0.0.0.0:5000/#/experiments/0?searchFilter=&orderByKey=attributes.start_time&orderByAsc=false&startTime=ALL&lifecycleFilter=Active&modelVersionFilter=All%20Runs&selectedColumns=attributes.%60Source%60,attributes.%60Models%60,attributes.%60Dataset%60&compareRunCharts=);
* models tracking: [MLFlow Models](http://0.0.0.0:5000/#/models).

Use the **experimental_scripts/test_service.ipynb** as an example of how to use the prediction service API. 

## Development guide
The application is containerized with Docker, therefore Docker Engine needs to be installed. 
Clone this repository:
```
git clone https://github.com/daniel-gheorghita/MLOps_car_price_prediction.git
```
Navigate to the source folder:
```
cd mlops_car_price_prediction
```
On a MacOS or Linux-based machine, you can simply run the  script:
```
./start_service.sh
```
Connect to the container (if needed) by running the  script:
```
./connect_to_docker.sh
```
To turn off the service, simply run:
```
./stop_service.sh
```
If any of these scripts cannot be executed, please run:
```
chmod +x <script_name>
```
Service monitoring:
* orchestration and scheduling: [Prefect Dashboard](http://0.0.0.0:4200/dashboard);
* experiments tracking: [MLFlow Experiments](http://0.0.0.0:5000/#/experiments/0?searchFilter=&orderByKey=attributes.start_time&orderByAsc=false&startTime=ALL&lifecycleFilter=Active&modelVersionFilter=All%20Runs&selectedColumns=attributes.%60Source%60,attributes.%60Models%60,attributes.%60Dataset%60&compareRunCharts=);
* models tracking: [MLFlow Models](http://0.0.0.0:5000/#/models).

Development via Notebook:
* access the [Notebook server](http://0.0.0.0:8888).

Or you can also connect via VSCode to the Docker container (if you install the required add-ons like Docker and SSH). 

## Troubleshoot

Sometimes the pipeline does not work because the Prefect Agent does not start (in spite of being started in the entrypoint script).
To solve this issue, connect to the Docker container by running
```
./connect_to_docker.sh
```
and run the same line below:
```
prefect agent start --pool default-agent-pool --work-queue default &
```

## Monitor the pipeline via dashboards

### Experiment tracking
Use this dashboard to inspect all the experiments and the training models.
![MLFlow Experiments](https://github.com/daniel-gheorghita/MLOps_car_price_prediction/blob/master/dashboards/mlflow_experiments.png)
### Model tracking
Use this dashboard to inspect the registered models.
![MLFlow models](https://github.com/daniel-gheorghita/MLOps_car_price_prediction/blob/master/dashboards/mlflow_models.png)
### Prefect dashboard
Use this dashboard to inspect the workflow.
![Prefect dashboard](https://github.com/daniel-gheorghita/MLOps_car_price_prediction/blob/master/dashboards/prefect_dashboard.png)
### Jupyter Notebook
Use this for development and experimenting with new code.
![Jupyter Notebook](https://github.com/daniel-gheorghita/MLOps_car_price_prediction/blob/master/dashboards/jupyter_notebook.png)
## Acknowledgements
As my dear wife is expecting and the due date is around the corner, I have made quite some sacrifices to follow this class and finish this project before the big B-Day. 
I am thankful for my wife's understanding of my slacking in household preparations, but I will make it up up to her as soon as I submit the project!
Also, thank you to the MLOps Zoomcamp instructors and organizers!

