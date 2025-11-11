# ===============================================================
# 📘 routes/mata_pelajaran_routes.py — Manajemen Mata Pelajaran (RBAC Protected)
# ===============================================================

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from core.permissions import authorize_access, check_permission
from main import db

router = APIRouter(
    prefix="/mata-pelajaran",
    tags=["Mata Pelajaran"],
    dependencies=[Depends(authorize_access)]  # ✅ Semua endpoint butuh JWT
)

# ===============================================================
# 📋 SCHEMA: Data Mata Pelajaran
# ===============================================================
class MataPelajaranCreate(BaseModel):
    kode_mapel: str | None = Field(default=None, description="Kode unik mapel, contoh: RPL101")
    nama_mapel: str = Field(..., description="Nama mata pelajaran, contoh: Algoritma dan Pemrograman")
    deskripsi: str | None = Field(default=None, description="Deskripsi singkat mata pelajaran")
    kategori: str = Field(default="Umum", description="Kategori pelajaran, contoh: Produktif / Umum")
    tingkat_kesulitan: str = Field(default="Pemula", description="Tingkat kesulitan: Pemula, Menengah, Lanjut")
    jurusan_id: int | None = Field(default=None, description="ID jurusan yang terkait (optional)")
    guru_id: int | None = Field(default=None, description="ID guru pengajar (optional)")


# ===============================================================
# 🧩 CREATE — Tambah Mata Pelajaran (Hanya Admin & Guru)
# ===============================================================
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_mata_pelajaran(data: MataPelajaranCreate, user=Depends(authorize_access)):
    check_permission(user, "mata_pelajaran")

    # 🔒 Murid tidak boleh create
    if user["role"] == "Murid":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Murid tidak memiliki izin untuk menambahkan mata pelajaran."
        )

    # ✅ Admin & Guru boleh
    try:
        created = await db.mata_pelajaran.create(data=data.dict())
        return {"message": "✅ Mata pelajaran berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat mata pelajaran: {str(e)}")


# ===============================================================
# 📜 READ — Ambil Semua Mata Pelajaran (Admin, Guru, Murid)
# ===============================================================
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_mata_pelajaran(user=Depends(authorize_access)):
    check_permission(user, "mata_pelajaran")

    try:
        if user["role"] == "Admin":
            # Admin: Semua mapel
            mapel_list = await db.mata_pelajaran.find_many(include={"guru": True, "jurusan": True})

        elif user["role"] == "Guru":
            # Guru: Mapel yang dia ajar
            guru = await db.guru.find_unique(where={"email": user["sub"]})
            if not guru:
                raise HTTPException(status_code=404, detail="Guru tidak ditemukan")
            mapel_list = await db.mata_pelajaran.find_many(
                where={"guru_id": guru.id},
                include={"guru": True, "jurusan": True}
            )

        else:
            # Murid: Semua mapel aktif (read-only)
            mapel_list = await db.mata_pelajaran.find_many(include={"guru": True, "jurusan": True})

        return {"total": len(mapel_list), "data": mapel_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data mata pelajaran: {str(e)}")


# ===============================================================
# 🔍 READ — Ambil Mata Pelajaran Berdasarkan ID (Semua Role)
# ===============================================================
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_mata_pelajaran(id: int, user=Depends(authorize_access)):
    check_permission(user, "mata_pelajaran")

    mapel = await db.mata_pelajaran.find_unique(
        where={"id": id},
        include={"guru": True, "jurusan": True}
    )

    if not mapel:
        raise HTTPException(status_code=404, detail="❌ Mata pelajaran tidak ditemukan")

    return {"data": mapel}


# ===============================================================
# ✏️ UPDATE — Ubah Mata Pelajaran (Hanya Admin & Guru)
# ===============================================================
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_mata_pelajaran(id: int, data: MataPelajaranCreate, user=Depends(authorize_access)):
    check_permission(user, "mata_pelajaran")

    # 🔒 Murid tidak boleh update
    if user["role"] == "Murid":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Murid tidak memiliki izin untuk memperbarui mata pelajaran."
        )

    existing = await db.mata_pelajaran.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Mata pelajaran tidak ditemukan")

    try:
        updated = await db.mata_pelajaran.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Mata pelajaran berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui mata pelajaran: {str(e)}")


# ===============================================================
# 🗑️ DELETE — Hapus Mata Pelajaran (Hanya Admin & Guru)
# ===============================================================
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_mata_pelajaran(id: int, user=Depends(authorize_access)):
    check_permission(user, "mata_pelajaran")

    # 🔒 Murid tidak boleh delete
    if user["role"] == "Murid":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Murid tidak memiliki izin untuk menghapus mata pelajaran."
        )

    existing = await db.mata_pelajaran.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Mata pelajaran tidak ditemukan")

    try:
        await db.mata_pelajaran.delete(where={"id": id})
        return {"message": "🗑️ Mata pelajaran berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus mata pelajaran: {str(e)}")
