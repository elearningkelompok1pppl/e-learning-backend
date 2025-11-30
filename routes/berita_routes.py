# routes/berita_routes.py — Manajemen Berita (RBAC Protected)
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime
from core.permissions import authorize_access
from main import db

router = APIRouter(
    tags=["Berita"],
    dependencies=[Depends(authorize_access)]  
)

# SCHEMA: Data Berita
class BeritaCreate(BaseModel):
    judul: str = Field(..., description="Judul berita")
    slug: str = Field(..., description="Slug unik untuk URL berita")
    konten: str = Field(..., description="Isi lengkap berita")
    kategori: str = Field(default="Pengumuman", description="Kategori berita")
    gambar_utama: str | None = Field(default=None, description="URL gambar utama")
    penulis_id: int | None = Field(default=None, description="ID penulis (Admin atau Guru)")
    penulis_tipe: str = Field(default="Admin", description="Jenis penulis: Admin atau Guru")
    status: str = Field(default="Draft", description="Status publikasi: Draft / Publish")
    tanggal_publish: datetime | None = Field(default=None, description="Tanggal berita dipublikasikan")

# CREATE — Tambah Berita Baru
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_berita(berita: BeritaCreate):
    try:
        created = await db.berita.create(data=berita.dict())
        return {"message": "✅ Berita berhasil dibuat", "data": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat berita: {str(e)}")

# READ — Ambil Semua Berita
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_berita():
    try:
        berita_list = await db.berita.find_many(
            include={"admin": True},
            order={"created_at": "desc"}
        )
        return {"total": len(berita_list), "data": berita_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil berita: {str(e)}")

# READ — Ambil Berita Berdasarkan ID
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_berita_by_id(id: int):
    berita = await db.berita.find_unique(
        where={"id": id},
        include={"admin": True}
    )

    if not berita:
        raise HTTPException(status_code=404, detail="❌ Berita tidak ditemukan")

    return {"data": berita}

# UPDATE — Ubah Berita Berdasarkan ID
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_berita(id: int, data: BeritaCreate):
    existing = await db.berita.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Berita tidak ditemukan")

    try:
        updated = await db.berita.update(where={"id": id}, data=data.dict())
        return {"message": "✅ Berita berhasil diperbarui", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui berita: {str(e)}")

# DELETE — Hapus Berita
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_berita(id: int):
    
    existing = await db.berita.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(status_code=404, detail="❌ Berita tidak ditemukan")

    try:
        await db.berita.delete(where={"id": id})
        return {"message": "🗑️ Berita berhasil dihapus"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus berita: {str(e)}")
