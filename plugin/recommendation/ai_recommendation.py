import os
from dotenv import load_dotenv
from google import genai

# Load env
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    raise ValueError("❗ GEMINI_API_KEY tidak ditemukan di .env")

# Client Gemini (SDK BARU)
client = genai.Client(api_key=GEMINI_KEY)

cluster_desc = {
    0: "Low Performer",
    1: "Average Performer",
    2: "High Performer"
}

def generate_recommendation_ai(student_name, cluster_label, data):
    kategori = cluster_desc.get(cluster_label, "Unknown")

    prompt = f"""
Konteks sistem:
Anda adalah AI asisten untuk guru dalam ekosistem e-learning sekolah.
Anda bertugas memberikan rekomendasi strategis berdasarkan performa siswa.
Jawaban harus singkat, actionable, dan langsung bisa dipakai guru.

Murid: {student_name}
Kategori Performansi: {kategori}

Data siswa:
{data}

Tugas Anda:
Tolong berikan rekomendasi dalam bentuk **3 bullet point**, berfokus pada:
- hal paling kritikal yang harus diperbaiki
- strategi belajar yang disarankan
- pendekatan hubungan guru–murid yang tepat

Format jawaban:
- poin rekomendasi 1
- poin rekomendasi 2
- poin rekomendasi 3

Bahasa: Indonesia.
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    text = response.text.strip()
    lines = [x.strip("-• ") for x in text.split("\n") if x.strip()]

    return lines[:3]
