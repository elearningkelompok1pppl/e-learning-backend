import numpy as np
from plugin.cluster.model_loader import load_model, load_scaler
from plugin.cluster.feature_schema import FEATURES

model = load_model()
scaler = load_scaler()

def predict_cluster_for_student(data_dict: dict):
    try:
        arr = np.array([data_dict[f] for f in FEATURES]).reshape(1, -1)
        arr_scaled = scaler.transform(arr)
        label = model.predict(arr_scaled)[0]
        return int(label)
    except Exception as e:
        print("⚠️ ERROR saat memprediksi: ", e)
        return None
