import os
from dotenv import load_dotenv
import google.generativeai as genai

# load env
load_dotenv()

# ambil API KEY
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    raise ValueError("❗ GEMINI_API_KEY tidak ditemukan di .env")

genai.configure(api_key=GEMINI_KEY)

cluster_desc = {
    0: "Low Performer",
    1: "Average Performer",
    2: "High Performer"
}

def generate_recommendation_ai(student_name, cluster_label, data):
    kategori = cluster_desc.get(cluster_label, "Unknown")

    prompt = f"""
Murid: {student_name}
Status: {kategori}

Data siswa:
{data}

Buat rekomendasi guru mencakup:
- saran akademik
- pendekatan komunikasi
- dukungan motivasi
- tindakan intervensi pembelajaran
- gaya umpan balik yang cocok
- tips spesifik sesuai profil murid

Jawab dengan bahasa Indonesia.
"""
    response = genai.GenerativeModel("gemini-2.5-flash").generate_content(prompt)
    return response.text
