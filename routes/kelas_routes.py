# routes/kelas_routes.py — Manajemen Kelas (RBAC Protected)
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from core.permissions import authorize_access, check_permission
from main import db

router = APIRouter(
    prefix="/kelas",
    tags=["Kelas"],
    dependencies=[Depends(authorize_access)]  # ✅ Semua endpoint butuh JWT
)

# SCHEMA: Data Kelas
class KelasCreate(BaseModel):
    nama_kelas: str = Field(..., description="Nama kelas, contoh: X RPL 1")
    tingkat: str = Field(..., description="Tingkat kelas, contoh: X / XI / XII")
    jurusan_id: int = Field(..., description="ID jurusan terkait")
    tahun_ajaran: str = Field(..., description="Tahun ajaran, contoh: 2024/2025")
    wali_kelas_id: int | None = Field(default=None, description="ID guru wali kelas")
    kapasitas: int | None = Field(default=36, description="Kapasitas maksimal murid")

# CREATE — Tambah Kelas (Hanya Admin)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_kelas(data: KelasCreate, user=Depends(authorize_access)):
    check_permission(user, "kelas")

    # Hanya Admin yang bisa create
    if user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Hanya Admin yang boleh menambahkan data kelas."
        )

    try:
        created = await db.kelas.create(data=data.dict())
        return {"message": "✅ Kelas berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat kelas: {str(e)}")

# READ — Ambil Semua Kelas (Admin, Guru, Murid)
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_kelas(user=Depends(authorize_access)):
    check_permission(user, "kelas")

    try:
        kelas_list = await db.kelas.find_many(
            include={"jurusan": True, "wali_kelas": True}
        )
        return {"total": len(kelas_list), "data": kelas_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data kelas: {str(e)}")

# READ — Ambil Kelas Berdasarkan ID (Admin, Guru, Murid)
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_kelas(id: int, user=Depends(authorize_access)):
    check_permission(user, "kelas")

    kelas = await db.kelas.find_unique(
        where={"id": id},
        include={"jurusan": True, "wali_kelas": True}
    )
    if not kelas:
        raise HTTPException(status_code=404, detail="❌ Kelas tidak ditemukan")
    return {"data": kelas}

# UPDATE — Ubah Data Kelas (Hanya Admin)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_kelas(id: int, data: KelasCreate, user=Depends(authorize_access)):
    check_permission(user, "kelas")

    # Hanya Admin yang boleh update
    if user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Hanya Admin yang boleh memperbarui data kelas."
        )

    existing = await db.kelas.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Kelas tidak ditemukan")

    try:
        updated = await db.kelas.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Kelas berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui kelas: {str(e)}")

# DELETE — Hapus Kelas (Hanya Admin)
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_kelas(id: int, user=Depends(authorize_access)):
    check_permission(user, "kelas")

    # Hanya Admin yang boleh delete
    if user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Hanya Admin yang boleh menghapus data kelas."
        )

    existing = await db.kelas.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Kelas tidak ditemukan")

    try:
        await db.kelas.delete(where={"id": id})
        return {"message": "🗑️ Kelas berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus kelas: {str(e)}")
