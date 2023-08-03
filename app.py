from flask import Flask, jsonify, request
import mlflow
import pandas as pd

app = Flask(__name__)

def load_latest_model():
    model_name = "car-price-predictor"
    model_version = "latest"
    try:
        model = mlflow.sklearn.load_model(model_uri=f"models:/{model_name}/{model_version}")
    except:
        model = None # or load a baseline model
    return model

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

@app.route('/predict', methods=['POST'])
def predict():
    json_ = request.json
    query_df = pd.DataFrame(json_)
    query = pd.get_dummies(query_df)
    query = query_df.values
    model = load_latest_model()
    if model is None:
     prediction = [0] * len(query) # or a baseline model prediction
    else:
     prediction = model.predict(query)
    return jsonify({'predicted_car_price': list(prediction)})

if __name__ == "__main__":
    # Connect to the MLFlow tracking server
    mlflow.set_tracking_uri("http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=8080, debug=True)
