# core/permissions.py — Role-Based Access Control (RBAC)
from fastapi import Depends, HTTPException, status
from core.security import get_current_user

# ROLE MATRIX — Definisi izin akses per role
ROLE_ACCESS = {
    # Admin bisa akses SEMUA modul
    "Admin": ["all"],

    # Guru: bisa kelola murid, tugas, absensi, quiz, hasil quiz, video, materi, dan kelasnya
    "Guru": [
        "murid",
        "kelas",
        "mata_pelajaran",
        "absensi",
        "tugas",
        "materi",
        "quiz",
        "soal_quiz",
        "hasil_quiz",
        "video",
        "pkl",
        "jurusan",
        "dashboard_guru",
        "cluster"
    ],

    # Murid: hanya bisa membaca data (read-only) di modul tertentu
    "Murid": [
        "kelas",
        "materi",
        "mata_pelajaran",  
        "quiz",
        "hasil_quiz",
        "tugas",
        "berita",
        "video",
        "jurusan",
    ],
}

# Authorization Middleware — Autentikasi Token JWT
async def authorize_access(user=Depends(get_current_user)):
    if not user or "role" not in user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="🔒 Unauthorized — token tidak valid atau tidak memiliki role.",
        )
    return user


# Permission Checker — Validasi Hak Akses
def check_permission(user: dict, module: str):
    role = user.get("role")

    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="❌ Role pengguna tidak ditemukan di token.",
        )

    # Ambil daftar izin berdasarkan role
    allowed_modules = ROLE_ACCESS.get(role, [])

    # Admin punya akses ke semua modul
    if "all" in allowed_modules:
        return True

    # Jika modul tidak ada di daftar izin role
    if module not in allowed_modules:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"🚫 Akses ditolak — {role} tidak memiliki izin untuk mengakses modul '{module}'.",
        )

    return True


# Helper — Cek apakah role memiliki akses penuh (optional)
def has_full_access(user: dict) -> bool:
    role = user.get("role")
    return "all" in ROLE_ACCESS.get(role, [])