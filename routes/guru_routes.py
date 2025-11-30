# routes/guru_routes.py — Manajemen Data Guru (RBAC Protected)

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from core.permissions import authorize_access, check_permission
from main import db

router = APIRouter(
    tags=["Guru"],
    dependencies=[Depends(authorize_access)]  
)

# SCHEMA: Data Guru
class GuruCreate(BaseModel):
    nama: str = Field(..., description="Nama lengkap guru")
    email: EmailStr = Field(..., description="Email unik guru")
    password: str = Field(..., description="Password guru (akan di-hash saat pendaftaran)")
    nip: str | None = Field(default=None, description="Nomor induk pegawai (opsional)")
    mata_pelajaran_text: str | None = Field(default=None, description="Deskripsi mata pelajaran yang diampu")
    foto_profil: str | None = Field(default=None, description="URL foto profil guru")
    no_telepon: str | None = Field(default=None, description="Nomor telepon guru")
    alamat: str | None = Field(default=None, description="Alamat lengkap guru")
    status: str = Field(default="Aktif", description="Status keaktifan guru (Aktif / Nonaktif)")

# CREATE — Tambah Guru Baru (Admin Only)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_guru(guru: GuruCreate, user=Depends(authorize_access)):
    check_permission(user, "guru") 

    if user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Hanya Admin yang boleh menambahkan data guru."
        )

    try:
        existing = await db.guru.find_unique(where={"email": guru.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email guru sudah terdaftar")

        created = await db.guru.create(data=guru.dict())
        return {"message": "✅ Guru berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat guru: {str(e)}")

# READ — Ambil Semua Data Guru
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_guru(user=Depends(authorize_access)):
    check_permission(user, "guru")

    # Murid tidak boleh akses daftar guru
    if user["role"] == "Murid":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Murid tidak memiliki izin untuk melihat data guru."
        )

    try:
        guru_list = await db.guru.find_many(order={"created_at": "desc"})
        return {"total": len(guru_list), "data": guru_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data guru: {str(e)}")

# READ — Ambil Guru Berdasarkan ID
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_guru_by_id(id: int, user=Depends(authorize_access)):
    check_permission(user, "guru")

    # ❌ Murid tidak boleh melihat detail guru
    if user["role"] == "Murid":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Murid tidak boleh mengakses data guru."
        )

    guru = await db.guru.find_unique(where={"id": id})
    if not guru:
        raise HTTPException(status_code=404, detail="❌ Guru tidak ditemukan")
    return {"data": guru}

# UPDATE — Ubah Data Guru (Admin Only)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_guru(id: int, data: GuruCreate, user=Depends(authorize_access)):
    check_permission(user, "guru")

    if user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Hanya Admin yang boleh memperbarui data guru."
        )

    existing = await db.guru.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Guru tidak ditemukan")

    try:
        updated = await db.guru.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Data guru berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui data guru: {str(e)}")

# DELETE — Hapus Guru (Admin Only)
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_guru(id: int, user=Depends(authorize_access)):
    check_permission(user, "guru")

    if user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Hanya Admin yang boleh menghapus guru."
        )

    existing = await db.guru.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Guru tidak ditemukan")

    try:
        await db.guru.delete(where={"id": id})
        return {"message": "🗑️ Guru berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus guru: {str(e)}")
