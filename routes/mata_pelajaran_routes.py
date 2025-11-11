from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from main import db

router = APIRouter()

class MataPelajaranCreate(BaseModel):
    kode_mapel: str | None = None
    nama_mapel: str
    deskripsi: str | None = None
    kategori: str = "Umum"
    tingkat_kesulitan: str = "Pemula"
    jurusan_id: int | None = None
    guru_id: int | None = None


@router.post("/")
async def create_mata_pelajaran(mapel: MataPelajaranCreate):
    try:
        created = await db.mata_pelajaran.create(data=mapel.dict())
        return {"message": "Mata pelajaran created successfully", "data": created}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/")
async def get_all_mata_pelajaran():
    return await db.mata_pelajaran.find_many(include={"guru": True, "jurusan": True})


@router.get("/{id}")
async def get_mata_pelajaran(id: int):
    mapel = await db.mata_pelajaran.find_unique(where={"id": id}, include={"guru": True, "jurusan": True})
    if not mapel:
        raise HTTPException(404, "Mata pelajaran not found")
    return mapel


@router.put("/{id}")
async def update_mata_pelajaran(id: int, data: MataPelajaranCreate):
    existing = await db.mata_pelajaran.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "Mata pelajaran not found")
    updated = await db.mata_pelajaran.update(where={"id": id}, data=data.dict())
    return {"message": "Mata pelajaran updated", "data": updated}


@router.delete("/{id}")
async def delete_mata_pelajaran(id: int):
    existing = await db.mata_pelajaran.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "Mata pelajaran not found")
    await db.mata_pelajaran.delete(where={"id": id})
    return {"message": "Mata pelajaran deleted successfully"}
