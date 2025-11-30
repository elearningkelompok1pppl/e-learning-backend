import pickle

MODEL_PATH = "models/MachineLearning/cluster_model.pkl"
SCALER_PATH = "models/MachineLearning/scaler.pkl"

def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def load_scaler():
    with open(SCALER_PATH, "rb") as f:
        return pickle.load(f)