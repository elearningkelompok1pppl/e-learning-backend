# ===============================================================
# 📘 routes/absensi_routes.py — Manajemen Absensi (RBAC Protected)
# ===============================================================

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime
from core.permissions import authorize_access
from main import db

router = APIRouter(
    tags=["Absensi"],
    dependencies=[Depends(authorize_access)]  # ✅ Semua endpoint butuh JWT
)


# ===============================================================
# 📋 SCHEMA: Data Absensi
# ===============================================================
class AbsensiCreate(BaseModel):
    murid_id: int | None = Field(default=None, description="ID murid (opsional)")
    kelas_id: int | None = Field(default=None, description="ID kelas (opsional)")
    mata_pelajaran_id: int | None = Field(default=None, description="ID mapel (opsional)")
    tanggal: datetime = Field(..., description="Tanggal absensi (YYYY-MM-DD)")
    status: str = Field(..., description="Status kehadiran: Hadir / Sakit / Izin / Alfa")
    keterangan: str | None = Field(default=None, description="Keterangan tambahan")
    guru_id: int | None = Field(default=None, description="Guru yang menginput absensi")

# ===============================================================
# 🧩 CREATE — Tambah Data Absensi (Hanya Guru)
# ===============================================================
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_absensi(data: AbsensiCreate, user=Depends(authorize_access)):
    role = user.get("role")

    if role != "Guru":
        raise HTTPException(status_code=403, detail="❌ Hanya Guru yang dapat membuat absensi")

    # Isi guru_id otomatis dari akun guru login
    guru = await db.guru.find_unique(where={"email": user["sub"]})
    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")
    data.guru_id = guru.id

    try:
        created = await db.absensi.create(data=data.dict())
        return {"message": "✅ Absensi berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat absensi: {str(e)}")

# ===============================================================
# 📜 READ — Ambil Semua Data Absensi
# ===============================================================
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_absensi(user=Depends(authorize_access)):
    role = user.get("role")

    try:
        # Guru dan Admin boleh melihat semua absensi
        if role in ["Guru", "Admin"]:
            absensi_list = await db.absensi.find_many(
                include={"murid": True, "kelas": True, "mata_pelajaran": True, "guru": True}
            )

        # Murid tidak boleh akses semua data absensi
        elif role == "Murid":
            raise HTTPException(status_code=403, detail="❌ Murid tidak boleh melihat seluruh data absensi")

        else:
            raise HTTPException(status_code=403, detail="❌ Akses ditolak")

        return {"total": len(absensi_list), "data": absensi_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data absensi: {str(e)}")

# ===============================================================
# 🔍 READ — Ambil Absensi Berdasarkan ID
# ===============================================================
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_absensi_by_id(id: int, user=Depends(authorize_access)):
    role = user.get("role")

    absensi = await db.absensi.find_unique(
        where={"id": id},
        include={"murid": True, "kelas": True, "mata_pelajaran": True, "guru": True}
    )

    if not absensi:
        raise HTTPException(status_code=404, detail="❌ Absensi tidak ditemukan")

    # Murid hanya boleh melihat absensinya sendiri
    if role == "Murid":
        murid = await db.murid.find_unique(where={"email": user["sub"]})
        if not murid or absensi.murid_id != murid.id:
            raise HTTPException(status_code=403, detail="❌ Tidak boleh melihat absensi milik orang lain")

    # Guru dan Admin bisa melihat semua
    return {"data": absensi}

# ===============================================================
# ✏️ UPDATE — Ubah Data Absensi (Hanya Guru)
# ===============================================================
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_absensi(id: int, data: AbsensiCreate, user=Depends(authorize_access)):
    role = user.get("role")

    if role != "Guru":
        raise HTTPException(status_code=403, detail="❌ Hanya Guru yang dapat memperbarui absensi")

    existing = await db.absensi.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Absensi tidak ditemukan")

    try:
        updated = await db.absensi.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Absensi berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui absensi: {str(e)}")

# ===============================================================
# 🗑️ DELETE — Hapus Data Absensi (Hanya Guru)
# ===============================================================
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_absensi(id: int, user=Depends(authorize_access)):
    role = user.get("role")

    if role != "Guru":
        raise HTTPException(status_code=403, detail="❌ Hanya Guru yang dapat menghapus absensi")

    existing = await db.absensi.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Absensi tidak ditemukan")

    try:
        await db.absensi.delete(where={"id": id})
        return {"message": "🗑️ Absensi berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus absensi: {str(e)}")