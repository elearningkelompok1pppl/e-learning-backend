# main.py — FastAPI + Prisma + JWT Authentication
from fastapi import FastAPI
from generated.prisma import Prisma
from fastapi.middleware.cors import CORSMiddleware 

# FastAPI Initialization
app = FastAPI(
    title="Sekolah API - FastAPI + Prisma + Neon + JWT Auth",
    description="Sistem API Sekolah berbasis FastAPI + Prisma ORM dengan PostgreSQL Neon Cloud & JWT Authentication",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],     
)

# Prisma Database Client (Single Shared Instance)
db = Prisma()

@app.on_event("startup")
async def startup():
    await db.connect()
    print("✅ Connected to Neon Database!")

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
    print("❌ Disconnected from Database.")

# --- Authentication Route (JWT) ---
from routes.auth_routes import router as auth_router

# --- Existing Routes ---
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

# --- New Routes Added ---
from routes.materi_routes import router as materi_router
from routes.quiz_routes import router as quiz_router
from routes.cluster_routes import router as cluster_router
from routes.soal_quiz_routes import router as soal_quiz_router
from routes.hasil_quiz_routes import router as hasil_quiz_router
from routes.dashboard_guru_routes import router as dashboard_guru_router
from routes.beranda_murid_routes import router as beranda_murid_router
# 🔗 Register All Routers

# --- Authentication ---
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# --- Core Data Routes ---
app.include_router(admin_router)  
app.include_router(guru_router, prefix="/guru", tags=["Guru"])
app.include_router(jurusan_router, prefix="/jurusan", tags=["Jurusan"])
app.include_router(kelas_router, prefix="/kelas", tags=["Kelas"])
app.include_router(murid_router, prefix="/murid", tags=["Murid"])
app.include_router(mata_pelajaran_router, prefix="/guru/mata-pelajaran", tags=["Mata Pelajaran"])
app.include_router(tugas_router, prefix="/tugas", tags=["Tugas"])
app.include_router(absensi_router, prefix="/absensi", tags=["Absensi"])
app.include_router(pkl_router, prefix="/pkl", tags=["PKL"])
app.include_router(berita_router, prefix="/berita", tags=["Berita"])
app.include_router(video_router, prefix="/video", tags=["Video"])

# --- Educational Content Routes ---
app.include_router(cluster_router, prefix="/cluster", tags=["Cluster"])
app.include_router(dashboard_guru_router, prefix="/dashboard-guru", tags=["Dashboard Guru"])
app.include_router(materi_router, prefix="/materi", tags=["Materi"])
app.include_router(quiz_router, prefix="/quiz", tags=["Quiz"])
app.include_router(soal_quiz_router, prefix="/soal-quiz", tags=["Soal Quiz"])
app.include_router(hasil_quiz_router, prefix="/hasil-quiz", tags=["Hasil Quiz"])
app.include_router(beranda_murid_router, prefix="/beranda-murid")


# Root Endpoint
@app.get("/")
def root():
    return {
        "message": "FastAPI + Prisma + Neon 🚀",
        "auth": "/auth/login",
        "docs_url": "/docs",
        "status": "connected",
        "author": "Fikhi Hakim",
        "project": "Sekolah API Backend",
    }
