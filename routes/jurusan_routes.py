from fastapi import APIRouter, HTTPException
from generated.prisma import Prisma
from pydantic import BaseModel
from main import db

router = APIRouter()

class JurusanCreate(BaseModel):
    kode_jurusan: str
    nama_jurusan: str
    deskripsi: str | None = None
    visi: str | None = None
    misi: str | None = None
    prospek_kerja: str | None = None
    foto_jurusan: str | None = None
    status: str = "Aktif"

@router.post("/")
async def create_jurusan(data: JurusanCreate):
    return await db.jurusan.create(data=data.dict())

@router.get("/")
async def get_all_jurusan():
    return await db.jurusan.find_many()

@router.get("/{id}")
async def get_jurusan(id: int):
    jurusan = await db.jurusan.find_unique(where={"id": id})
    if not jurusan:
        raise HTTPException(404, "Jurusan not found")
    return jurusan

@router.put("/{id}")
async def update_jurusan(id: int, data: JurusanCreate):
    updated = await db.jurusan.update(where={"id": id}, data=data.dict())
    return {"message": "Jurusan updated", "data": updated}

@router.delete("/{id}")
async def delete_jurusan(id: int):
    await db.jurusan.delete(where={"id": id})
    return {"message": "Jurusan deleted"}
