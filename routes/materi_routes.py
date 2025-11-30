# ===============================================================
# 📘 routes/materi_routes.py — Manajemen Materi Belajar (RBAC Protected)
# ===============================================================

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from core.permissions import authorize_access, check_permission
from main import db

router = APIRouter(
    tags=["Materi"],
    dependencies=[Depends(authorize_access)]  # ✅ Semua endpoint butuh JWT
)

# ===============================================================
# 📋 SCHEMA: Data Materi
# ===============================================================
class MateriCreate(BaseModel):
    judul: str = Field(..., description="Judul materi pembelajaran")
    konten: str = Field(..., description="Konten utama materi")
    file_materi: str | None = Field(default=None, description="URL atau nama file materi (opsional)")
    tipe_file: str | None = Field(default=None, description="Tipe file materi, misal: PDF, Video, PPT")
    mata_pelajaran_id: int | None = Field(default=None, description="ID mata pelajaran terkait")
    guru_id: int | None = Field(default=None, description="ID guru pengunggah materi")
    kelas_id: int | None = Field(default=None, description="ID kelas target materi")

# ===============================================================
# 🧩 CREATE — Tambah Materi (Admin & Guru)
# ===============================================================
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_materi(data: MateriCreate, user=Depends(authorize_access)):
    role = user.get("role")

    # ✅ Hanya Admin atau Guru boleh membuat
    if role not in ["Admin", "Guru"]:
        raise HTTPException(
            status_code=403,
            detail="❌ Akses ditolak — hanya Admin atau Guru yang bisa membuat materi"
        )

    # Jika Guru, isi otomatis guru_id berdasarkan token login
    if role == "Guru" and not data.guru_id:
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru:
            raise HTTPException(status_code=404, detail="Guru tidak ditemukan")
        data.guru_id = guru.id

    try:
        created = await db.materi.create(data=data.dict())
        return {"message": "✅ Materi berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat materi: {str(e)}")

# ===============================================================
# 📜 READ — Ambil Semua Materi (Admin, Guru, Murid)
# ===============================================================
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_materi(user=Depends(authorize_access)):
    role = user.get("role")

    try:
        # Admin → semua materi
        if role == "Admin":
            materi_list = await db.materi.find_many(
                include={"mata_pelajaran": True, "guru": True, "kelas": True}
            )

        # Guru → semua materi yang diunggahnya sendiri
        elif role == "Guru":
            guru = await db.guru.find_unique(where={"email": user["sub"]})
            if not guru:
                raise HTTPException(status_code=404, detail="Guru tidak ditemukan")
            materi_list = await db.materi.find_many(
                where={"guru_id": guru.id},
                include={"mata_pelajaran": True, "kelas": True}
            )

        # Murid → hanya boleh baca semua (read-only)
        else:
            materi_list = await db.materi.find_many(
                include={"mata_pelajaran": True, "guru": True, "kelas": True}
            )

        return {"total": len(materi_list), "data": materi_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data materi: {str(e)}")

# 🔍 READ — Ambil Materi Berdasarkan ID (Semua Role)
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_materi(id: int, user=Depends(authorize_access)):
    materi = await db.materi.find_unique(
        where={"id": id},
        include={"guru": True, "mata_pelajaran": True, "kelas": True}
    )
    if not materi:
        raise HTTPException(status_code=404, detail="❌ Materi tidak ditemukan")
    return {"data": materi}

# UPDATE — Ubah Materi (Admin & Guru)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_materi(id: int, data: MateriCreate, user=Depends(authorize_access)):
    role = user.get("role")
    existing = await db.materi.find_unique(where={"id": id})

    if not existing:
        raise HTTPException(status_code=404, detail="❌ Materi tidak ditemukan")

    # Murid tidak boleh ubah
    if role == "Murid":
        raise HTTPException(
            status_code=403,
            detail="❌ Murid tidak memiliki izin untuk mengubah materi."
        )

    # Guru hanya bisa ubah materi miliknya sendiri
    if role == "Guru":
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru or existing.guru_id != guru.id:
            raise HTTPException(
                status_code=403,
                detail="❌ Guru tidak bisa mengubah materi milik orang lain."
            )

    try:
        updated = await db.materi.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Materi berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui materi: {str(e)}")

# DELETE — Hapus Materi (Admin & Guru)
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_materi(id: int, user=Depends(authorize_access)):
    role = user.get("role")
    existing = await db.materi.find_unique(where={"id": id})

    if not existing:
        raise HTTPException(status_code=404, detail="❌ Materi tidak ditemukan")

    # Murid tidak boleh hapus
    if role == "Murid":
        raise HTTPException(
            status_code=403,
            detail="❌ Murid tidak memiliki izin untuk menghapus materi."
        )

    # Guru hanya bisa hapus materi miliknya sendiri
    if role == "Guru":
        guru = await db.guru.find_unique(where={"email": user["sub"]})
        if not guru or existing.guru_id != guru.id:
            raise HTTPException(
                status_code=403,
                detail="❌ Guru tidak bisa menghapus materi milik orang lain."
            )

    try:
        await db.materi.delete(where={"id": id})
        return {"message": "🗑️ Materi berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus materi: {str(e)}")
