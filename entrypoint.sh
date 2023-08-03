#!/bin/sh
make quality_checks &
mlflow server --host 0.0.0.0 --backend-store-uri sqlite:///mydb.sqlite &
python3 /app/app.py &
prefect server start --host 0.0.0.0 &
sleep 5
python3 /app/flows/create_prefect_deployments.py &
jupyter notebook --ip 0.0.0.0 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password='' &
sleep 10
prefect agent start --pool default-agent-pool --work-queue default &
sleep 500
make test &
sleep infinity
