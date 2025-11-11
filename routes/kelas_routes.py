from fastapi import APIRouter, HTTPException
from generated.prisma import Prisma
from pydantic import BaseModel
from main import db

router = APIRouter()

class KelasCreate(BaseModel):
    nama_kelas: str
    tingkat: str
    jurusan_id: int
    tahun_ajaran: str
    wali_kelas_id: int | None = None
    kapasitas: int | None = 36

@router.post("/")
async def create_kelas(data: KelasCreate):
    return await db.kelas.create(data=data.dict())

@router.get("/")
async def get_all_kelas():
    return await db.kelas.find_many(include={"jurusan": True, "wali_kelas": True})

@router.get("/{id}")
async def get_kelas(id: int):
    kelas = await db.kelas.find_unique(where={"id": id}, include={"jurusan": True, "wali_kelas": True})
    if not kelas:
        raise HTTPException(404, "Kelas not found")
    return kelas

@router.put("/{id}")
async def update_kelas(id: int, data: KelasCreate):
    updated = await db.kelas.update(where={"id": id}, data=data.dict())
    return {"message": "Kelas updated", "data": updated}

@router.delete("/{id}")
async def delete_kelas(id: int):
    await db.kelas.delete(where={"id": id})
    return {"message": "Kelas deleted"}
