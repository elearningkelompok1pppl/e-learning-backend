# ===============================================================
# 📘 routes/tugas_routes.py — Manajemen Tugas (RBAC Protected)
# ===============================================================

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime
from core.permissions import authorize_access
from main import db

router = APIRouter(
    prefix="/tugas",
    tags=["Tugas"],
    dependencies=[Depends(authorize_access)]  # ✅ Semua endpoint butuh JWT
)

# ===============================================================
# 📋 SCHEMA: Data Tugas
# ===============================================================
class TugasCreate(BaseModel):
    judul: str = Field(..., description="Judul tugas")
    deskripsi: str | None = Field(default=None, description="Deskripsi tugas")
    mata_pelajaran_id: int | None = Field(default=None, description="ID mata pelajaran")
    kelas_id: int | None = Field(default=None, description="ID kelas")
    guru_id: int | None = Field(default=None, description="ID guru pembuat tugas")
    deadline: datetime | None = Field(default=None, description="Batas pengumpulan tugas")
    bobot: int | None = Field(default=100, description="Bobot nilai tugas")
    file_tugas: str | None = Field(default=None, description="File tugas jika ada")
    status: str = Field(default="Active", description="Status tugas (Active/Closed)")

# ===============================================================
# 🧩 CREATE — Tambah Tugas (Hanya Guru)
# ===============================================================
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_tugas(data: TugasCreate, user=Depends(authorize_access)):
    role = user.get("role")

    # ❌ Hanya Guru yang boleh membuat tugas
    if role != "Guru":
        raise HTTPException(status_code=403, detail="❌ Hanya Guru yang dapat membuat tugas")

    # ✅ Isi guru_id otomatis berdasarkan akun login
    guru = await db.guru.find_unique(where={"email": user["sub"]})
    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    data.guru_id = guru.id

    try:
        created = await db.tugas.create(data=data.dict())
        return {"message": "✅ Tugas berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat tugas: {str(e)}")

# ===============================================================
# 📜 READ — Ambil Semua Tugas (Admin, Guru, Murid)
# ===============================================================
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_tugas(user=Depends(authorize_access)):
    role = user.get("role")

    try:
        if role == "Guru":
            # Guru -> hanya tugas yang dia buat
            guru = await db.guru.find_unique(where={"email": user["sub"]})
            if not guru:
                raise HTTPException(status_code=404, detail="Guru tidak ditemukan")
            tugas_list = await db.tugas.find_many(
                where={"guru_id": guru.id},
                include={"kelas": True, "mata_pelajaran": True}
            )

        elif role == "Murid":
            # Murid -> hanya tugas untuk kelasnya
            murid = await db.murid.find_unique(where={"email": user["sub"]}, include={"kelas": True})
            if not murid:
                raise HTTPException(status_code=404, detail="Murid tidak ditemukan")
            tugas_list = await db.tugas.find_many(
                where={"kelas_id": murid.kelas_id},
                include={"guru": True, "mata_pelajaran": True}
            )

        elif role == "Admin":
            # Admin -> hanya read semua tugas
            tugas_list = await db.tugas.find_many(
                include={"guru": True, "kelas": True, "mata_pelajaran": True}
            )

        else:
            raise HTTPException(status_code=403, detail="❌ Akses ditolak")

        return {"total": len(tugas_list), "data": tugas_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data tugas: {str(e)}")

# ===============================================================
# 🔍 READ — Ambil Tugas Berdasarkan ID (Admin, Guru, Murid)
# ===============================================================
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_tugas(id: int, user=Depends(authorize_access)):
    tugas = await db.tugas.find_unique(
        where={"id": id},
        include={"guru": True, "kelas": True, "mata_pelajaran": True}
    )

    if not tugas:
        raise HTTPException(status_code=404, detail="❌ Tugas tidak ditemukan")

    # Murid hanya boleh melihat tugas dari kelasnya
    if user.get("role") == "Murid":
        murid = await db.murid.find_unique(where={"email": user["sub"]}, include={"kelas": True})
        if not murid or tugas.kelas_id != murid.kelas_id:
            raise HTTPException(status_code=403, detail="❌ Tidak boleh melihat tugas dari kelas lain")

    return {"data": tugas}

# UPDATE — Ubah Tugas (Hanya Guru Pemilik)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_tugas(id: int, data: TugasCreate, user=Depends(authorize_access)):
    role = user.get("role")

    if role != "Guru":
        raise HTTPException(status_code=403, detail="❌ Hanya Guru yang boleh memperbarui tugas")

    existing = await db.tugas.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Tugas tidak ditemukan")

    guru = await db.guru.find_unique(where={"email": user["sub"]})
    if not guru or existing.guru_id != guru.id:
        raise HTTPException(status_code=403, detail="❌ Tidak boleh memperbarui tugas milik guru lain")

    try:
        updated = await db.tugas.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Tugas berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui tugas: {str(e)}")

# DELETE — Hapus Tugas (Hanya Guru Pemilik)
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_tugas(id: int, user=Depends(authorize_access)):
    role = user.get("role")

    if role != "Guru":
        raise HTTPException(status_code=403, detail="❌ Hanya Guru yang boleh menghapus tugas")

    existing = await db.tugas.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Tugas tidak ditemukan")

    guru = await db.guru.find_unique(where={"email": user["sub"]})
    if not guru or existing.guru_id != guru.id:
        raise HTTPException(status_code=403, detail="❌ Tidak boleh menghapus tugas milik guru lain")

    try:
        await db.tugas.delete(where={"id": id})
        return {"message": "🗑️ Tugas berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus tugas: {str(e)}")
