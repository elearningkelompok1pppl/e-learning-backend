# main.py
from fastapi import FastAPI
from generated.prisma import Prisma

# ===============================================================
# 🚀 FastAPI Initialization
# ===============================================================
app = FastAPI(
    title="Sekolah API - FastAPI + Prisma + Neon",
    description="Sistem API Sekolah berbasis FastAPI + Prisma ORM dengan database PostgreSQL Neon Cloud",
    version="1.0.0"
)

# ===============================================================
# 🗃️ Prisma Database Client (Single Shared Instance)
# ===============================================================
db = Prisma()

@app.on_event("startup")
async def startup():
    """Connect to the database on app startup."""
    await db.connect()
    print("✅ Connected to Neon Database!")

@app.on_event("shutdown")
async def shutdown():
    """Disconnect database on app shutdown."""
    await db.disconnect()
    print("❌ Disconnected from Database.")


# ===============================================================
# 📦 Import Routers (after db instance created)
# ===============================================================
# NOTE:
#  Each route file should import db using:  `from main import db`

# Existing routes
from routes.admin_routes import router as admin_router
from routes.guru_routes import router as guru_router
from routes.jurusan_routes import router as jurusan_router
from routes.kelas_routes import router as kelas_router
from routes.murid_routes import router as murid_router
from routes.mata_pelajaran_routes import router as mata_pelajaran_router
from routes.tugas_routes import router as tugas_router
from routes.absensi_routes import router as absensi_router
from routes.pkl_routes import router as pkl_router
from routes.berita_routes import router as berita_router
from routes.video_routes import router as video_router

# ✅ New routes (baru ditambahkan)
from routes.materi_routes import router as materi_router
from routes.quiz_routes import router as quiz_router
from routes.soal_quiz_routes import router as soal_quiz_router
from routes.hasil_quiz_routes import router as hasil_quiz_router



# ===============================================================
# 🔗 Register All Routers
# ===============================================================
# --- Existing ---
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(guru_router, prefix="/guru", tags=["Guru"])
app.include_router(jurusan_router, prefix="/jurusan", tags=["Jurusan"])
app.include_router(kelas_router, prefix="/kelas", tags=["Kelas"])
app.include_router(murid_router, prefix="/murid", tags=["Murid"])
app.include_router(mata_pelajaran_router, prefix="/mata-pelajaran", tags=["Mata Pelajaran"])
app.include_router(tugas_router, prefix="/tugas", tags=["Tugas"])
app.include_router(absensi_router, prefix="/absensi", tags=["Absensi"])
app.include_router(pkl_router, prefix="/pkl", tags=["PKL"])
app.include_router(berita_router, prefix="/berita", tags=["Berita"])
app.include_router(video_router, prefix="/video", tags=["Video"])

# --- New Routes Added ---
app.include_router(materi_router, prefix="/materi", tags=["Materi"])
app.include_router(quiz_router, prefix="/quiz", tags=["Quiz"])
app.include_router(soal_quiz_router, prefix="/soal-quiz", tags=["Soal Quiz"])
app.include_router(hasil_quiz_router, prefix="/hasil-quiz", tags=["Hasil Quiz"])


# ===============================================================
# 🏠 Root Endpoint
# ===============================================================
@app.get("/")
def root():
    return {
        "message": "FastAPI + Prisma + Neon 🚀",
        "status": "connected",
        "docs_url": "/docs",
        "author": "Fikhi Hakim",
        "project": "Sekolah API Backend",
    }
