import numpy as np
from plugin.cluster.model_loader import load_model, load_scaler
from plugin.cluster.feature_schema import FEATURES

model = load_model()
scaler = load_scaler()
import numpy as np

DEFAULT_VALUE = 0  # atau bisa 50, atau rata-rata dataset

def predict_cluster_for_student(data_dict: dict):
    try:
        cleaned = {}
        for f in FEATURES:
            val = data_dict.get(f)

            if val is None or val == "" or val == "null":
                cleaned[f] = DEFAULT_VALUE
            else:
                cleaned[f] = float(val)

        arr = np.array([cleaned[f] for f in FEATURES]).reshape(1, -1)
        arr_scaled = scaler.transform(arr)
        label = model.predict(arr_scaled)[0]
        return int(label)

    except Exception as e:
        print("⚠️ ERROR saat memprediksi:", e)
        return None