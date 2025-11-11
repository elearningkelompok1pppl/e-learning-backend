from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from main import db

router = APIRouter()

class BeritaCreate(BaseModel):
    judul: str
    slug: str
    konten: str
    kategori: str = "Pengumuman"
    gambar_utama: str | None = None
    penulis_id: int | None = None
    penulis_tipe: str = "Admin"
    status: str = "Draft"
    tanggal_publish: datetime | None = None


@router.post("/")
async def create_berita(berita: BeritaCreate):
    try:
        created = await db.berita.create(data=berita.dict())
        return {"message": "Berita created successfully", "data": created}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/")
async def get_all_berita():
    return await db.berita.find_many(include={"admin": True})


@router.get("/{id}")
async def get_berita(id: int):
    berita = await db.berita.find_unique(where={"id": id}, include={"admin": True})
    if not berita:
        raise HTTPException(404, "Berita not found")
    return berita


@router.put("/{id}")
async def update_berita(id: int, data: BeritaCreate):
    existing = await db.berita.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "Berita not found")
    updated = await db.berita.update(where={"id": id}, data=data.dict())
    return {"message": "Berita updated", "data": updated}


@router.delete("/{id}")
async def delete_berita(id: int):
    existing = await db.berita.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "Berita not found")
    await db.berita.delete(where={"id": id})
    return {"message": "Berita deleted successfully"}
