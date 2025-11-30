# routes/pkl_routes.py — Manajemen PKL (RBAC Protected)
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime
from core.permissions import authorize_access, check_permission
from main import db

router = APIRouter(
    tags=["PKL"],
    dependencies=[Depends(authorize_access)] 
)

#  SCHEMA: Data PKL
class PKLCreate(BaseModel):
    murid_id: int | None = Field(default=None, description="ID murid peserta PKL")
    partner_id: int | None = Field(default=None, description="ID mitra industri tempat PKL")
    jurusan_id: int | None = Field(default=None, description="ID jurusan terkait PKL")
    tanggal_mulai: datetime | None = Field(default=None, description="Tanggal mulai PKL")
    tanggal_selesai: datetime | None = Field(default=None, description="Tanggal selesai PKL")
    pembimbing_sekolah_id: int | None = Field(default=None, description="ID guru pembimbing sekolah")
    pembimbing_industri: str | None = Field(default=None, description="Nama pembimbing industri")
    nilai: float | None = Field(default=None, description="Nilai akhir PKL")
    keterangan: str | None = Field(default=None, description="Catatan tambahan")
    status: str = Field(default="Sedang Berjalan", description="Status PKL")


# CREATE — Tambah Data PKL (Hanya Admin)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_pkl(pkl: PKLCreate, user=Depends(authorize_access)):
    check_permission(user, "pkl")  

    try:
        created = await db.pkl.create(data=pkl.dict())
        return {"message": "✅ PKL berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat data PKL: {str(e)}")


# READ — Ambil Semua Data PKL (Admin, Guru, Murid)
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_pkl(user=Depends(authorize_access)):
    role = user.get("role")

    try:
        # Admin → semua data
        if role == "Admin":
            pkl_list = await db.pkl.find_many(include={"murid": True, "partner": True, "jurusan": True, "pembimbing_sekolah": True})

        # Guru → hanya PKL yang dibimbing olehnya
        elif role == "Guru":
            guru = await db.guru.find_unique(where={"email": user["sub"]})
            if not guru:
                raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

            pkl_list = await db.pkl.find_many(
                where={"pembimbing_sekolah_id": guru.id},
                include={"murid": True, "partner": True, "jurusan": True}
            )

        # Murid → hanya PKL dirinya sendiri
        elif role == "Murid":
            murid = await db.murid.find_unique(where={"email": user["sub"]})
            if not murid:
                raise HTTPException(status_code=404, detail="Murid tidak ditemukan")

            pkl_list = await db.pkl.find_many(
                where={"murid_id": murid.id},
                include={"partner": True, "jurusan": True, "pembimbing_sekolah": True}
            )
        else:
            raise HTTPException(status_code=403, detail="Akses ditolak")

        return {"total": len(pkl_list), "data": pkl_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data PKL: {str(e)}")


# READ — Ambil PKL Berdasarkan ID
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_pkl(id: int, user=Depends(authorize_access)):
    role = user.get("role")

    pkl = await db.pkl.find_unique(
        where={"id": id},
        include={"murid": True, "partner": True, "jurusan": True, "pembimbing_sekolah": True}
    )

    if not pkl:
        raise HTTPException(status_code=404, detail="❌ PKL tidak ditemukan")

    # 🧩 Pembatasan akses
    if role == "Murid" and pkl.murid.email != user["sub"]:
        raise HTTPException(status_code=403, detail="❌ Tidak boleh melihat PKL murid lain")
    if role == "Guru" and (pkl.pembimbing_sekolah and pkl.pembimbing_sekolah.email != user["sub"]):
        raise HTTPException(status_code=403, detail="❌ Tidak boleh melihat PKL bukan bimbingannya")

    return {"data": pkl}


# UPDATE — Ubah Data PKL (Admin, Guru Pembimbing, Murid Sendiri)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_pkl(id: int, data: PKLCreate, user=Depends(authorize_access)):
    role = user.get("role")
    existing = await db.pkl.find_unique(where={"id": id})

    if not existing:
        raise HTTPException(status_code=404, detail="❌ PKL tidak ditemukan")

    if role == "Murid":
        murid = await db.murid.find_unique(where={"email": user["sub"]})
        if not murid or existing.murid_id != murid.id:
            raise HTTPException(status_code=403, detail="❌ Tidak boleh mengedit PKL murid lain")

    if role == "Guru":
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru or existing.pembimbing_sekolah_id != guru.id:
            raise HTTPException(status_code=403, detail="❌ Tidak boleh mengedit PKL bimbingan guru lain")

    if role not in ["Admin", "Guru", "Murid"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")

    try:
        updated = await db.pkl.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Data PKL berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui data PKL: {str(e)}")


# DELETE — Hapus Data PKL (Hanya Admin)
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_pkl(id: int, user=Depends(authorize_access)):
    check_permission(user, "pkl")  # ✅ Hanya Admin

    existing = await db.pkl.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ PKL tidak ditemukan")

    try:
        await db.pkl.delete(where={"id": id})
        return {"message": "🗑️ PKL berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus data PKL: {str(e)}")
