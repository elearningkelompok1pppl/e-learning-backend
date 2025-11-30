# routes/jurusan_routes.py — Manajemen Jurusan (RBAC Protected)
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from core.permissions import authorize_access, check_permission
from main import db

router = APIRouter(
    tags=["Jurusan"],
    dependencies=[Depends(authorize_access)]  
)

# SCHEMA: Data Jurusan
class JurusanCreate(BaseModel):
    kode_jurusan: str = Field(..., description="Kode unik untuk jurusan, misal: TKJ, RPL")
    nama_jurusan: str = Field(..., description="Nama jurusan, misal: Rekayasa Perangkat Lunak")
    deskripsi: str | None = Field(default=None, description="Deskripsi singkat jurusan")
    visi: str | None = Field(default=None, description="Visi jurusan")
    misi: str | None = Field(default=None, description="Misi jurusan")
    prospek_kerja: str | None = Field(default=None, description="Prospek kerja lulusan")
    foto_jurusan: str | None = Field(default=None, description="URL foto jurusan")
    status: str = Field(default="Aktif", description="Status jurusan (Aktif / Nonaktif)")

# CREATE — Tambah Jurusan (Hanya Admin)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_jurusan(data: JurusanCreate, user=Depends(authorize_access)):
    check_permission(user, "jurusan")

    # Hanya Admin yang boleh Create
    if user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Hanya Admin yang boleh menambahkan jurusan."
        )

    try:
        created = await db.jurusan.create(data=data.dict())
        return {"message": "✅ Jurusan berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat jurusan: {str(e)}")

# 📜 READ — Ambil Semua Jurusan (Admin, Guru, Murid)
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_jurusan(user=Depends(authorize_access)):
    check_permission(user, "jurusan")

    try:
        jurusan_list = await db.jurusan.find_many()
        return {"total": len(jurusan_list), "data": jurusan_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data jurusan: {str(e)}")

# 🔍 READ — Ambil Jurusan Berdasarkan ID (Admin, Guru, Murid)
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_jurusan(id: int, user=Depends(authorize_access)):
    check_permission(user, "jurusan")

    jurusan = await db.jurusan.find_unique(where={"id": id})
    if not jurusan:
        raise HTTPException(status_code=404, detail="❌ Jurusan tidak ditemukan")
    return {"data": jurusan}

# UPDATE — Ubah Jurusan (Hanya Admin)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_jurusan(id: int, data: JurusanCreate, user=Depends(authorize_access)):
    check_permission(user, "jurusan")

    # Hanya Admin yang boleh Update
    if user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Hanya Admin yang boleh memperbarui data jurusan."
        )

    existing = await db.jurusan.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Jurusan tidak ditemukan")

    try:
        updated = await db.jurusan.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Jurusan berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui jurusan: {str(e)}")

# DELETE — Hapus Jurusan (Hanya Admin)
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_jurusan(id: int, user=Depends(authorize_access)):
    check_permission(user, "jurusan")

    # Hanya Admin yang boleh Delete
    if user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Hanya Admin yang boleh menghapus jurusan."
        )

    existing = await db.jurusan.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Jurusan tidak ditemukan")

    try:
        await db.jurusan.delete(where={"id": id})
        return {"message": "🗑️ Jurusan berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus jurusan: {str(e)}")
