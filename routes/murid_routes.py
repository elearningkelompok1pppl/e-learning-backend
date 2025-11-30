# routes/murid_routes.py — Manajemen Data Murid (RBAC Protected)

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from core.permissions import authorize_access, check_permission
from main import db

router = APIRouter(
    tags=["Murid"],
    dependencies=[Depends(authorize_access)]  # ✅ Semua endpoint butuh JWT
)

# SCHEMA: Data Murid
class MuridCreate(BaseModel):
    nama: str = Field(..., description="Nama lengkap murid")
    email: str = Field(..., description="Email murid")
    password: str = Field(..., description="Password murid")
    nis: str | None = Field(default=None, description="Nomor Induk Siswa (opsional)")
    nisn: str | None = Field(default=None, description="Nomor Induk Siswa Nasional (opsional)")
    kelas_id: int | None = Field(default=None, description="ID kelas murid")
    jurusan_id: int | None = Field(default=None, description="ID jurusan murid")
    jenis_kelamin: str | None = Field(default=None, description="Laki-laki / Perempuan")
    alamat: str | None = Field(default=None, description="Alamat rumah murid")
    no_telepon: str | None = Field(default=None, description="Nomor telepon murid")

# CREATE — Tambah Murid (Hanya Admin)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_murid(data: MuridCreate, user=Depends(authorize_access)):
    check_permission(user, "murid")  # ✅ Hanya Admin

    try:
        existing = await db.murid.find_unique(where={"email": data.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email murid sudah terdaftar")

        created = await db.murid.create(data=data.dict())
        return {"message": "✅ Murid berhasil ditambahkan", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menambahkan murid: {str(e)}")

# READ — Ambil Semua Murid (Admin & Guru)
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_murid(user=Depends(authorize_access)):
    role = user.get("role")

    try:
        # Admin -> semua murid
        if role == "Admin":
            murid_list = await db.murid.find_many(include={"kelas": True, "jurusan": True})

        # Guru -> hanya murid di kelas yang dia ajar (kalau ada)
        elif role == "Guru":
            guru = await db.guru.find_unique(where={"email": user["sub"]})
            if not guru:
                raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

            murid_list = await db.murid.find_many(
                where={"kelas": {"wali_kelas_id": guru.id}},
                include={"kelas": True, "jurusan": True},
            )

        # Murid -> hanya dirinya sendiri
        elif role == "Murid":
            murid = await db.murid.find_unique(where={"email": user["sub"]})
            if not murid:
                raise HTTPException(status_code=404, detail="Murid tidak ditemukan")
            murid_list = [murid]
        else:
            raise HTTPException(status_code=403, detail="Akses ditolak")

        return {"total": len(murid_list), "data": murid_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data murid: {str(e)}")

# READ — Ambil Murid Berdasarkan ID (Admin, Guru, Murid Sendiri)
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_murid(id: int, user=Depends(authorize_access)):
    role = user.get("role")
    murid = await db.murid.find_unique(where={"id": id}, include={"kelas": True, "jurusan": True})

    if not murid:
        raise HTTPException(status_code=404, detail="❌ Murid tidak ditemukan")

    # 🔒 Jika Murid, hanya boleh akses datanya sendiri
    if role == "Murid" and murid.email != user["sub"]:
        raise HTTPException(status_code=403, detail="❌ Tidak boleh melihat data murid lain")

    return {"data": murid}

# UPDATE — Ubah Data Murid (Admin & Murid Sendiri)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_murid(id: int, data: MuridCreate, user=Depends(authorize_access)):
    role = user.get("role")
    existing = await db.murid.find_unique(where={"id": id})

    if not existing:
        raise HTTPException(status_code=404, detail="❌ Murid tidak ditemukan")

    # 🧠 Murid hanya boleh update dirinya sendiri
    if role == "Murid" and existing.email != user["sub"]:
        raise HTTPException(status_code=403, detail="❌ Tidak boleh mengubah data murid lain")

    # 🧠 Guru tidak boleh mengedit data murid
    if role == "Guru":
        raise HTTPException(status_code=403, detail="❌ Guru tidak boleh mengubah data murid")

    try:
        updated = await db.murid.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Data murid berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui data murid: {str(e)}")

# DELETE — Hapus Murid (Hanya Admin)
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_murid(id: int, user=Depends(authorize_access)):
    check_permission(user, "murid")  # ✅ Hanya Admin

    existing = await db.murid.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Murid tidak ditemukan")

    try:
        await db.murid.delete(where={"id": id})
        return {"message": "🗑️ Murid berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus murid: {str(e)}")
