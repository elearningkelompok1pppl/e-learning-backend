from fastapi import APIRouter, HTTPException
from generated.prisma import Prisma
from pydantic import BaseModel
from main import db

router = APIRouter()

class MuridCreate(BaseModel):
    nama: str
    email: str
    password: str
    nis: str | None = None
    nisn: str | None = None
    kelas_id: int | None = None
    jurusan_id: int | None = None
    jenis_kelamin: str | None = None
    alamat: str | None = None
    no_telepon: str | None = None

@router.post("/")
async def create_murid(data: MuridCreate):
    return await db.murid.create(data=data.dict())

@router.get("/")
async def get_all_murid():
    return await db.murid.find_many(include={"kelas": True, "jurusan": True})

@router.get("/{id}")
async def get_murid(id: int):
    murid = await db.murid.find_unique(where={"id": id}, include={"kelas": True, "jurusan": True})
    if not murid:
        raise HTTPException(404, "Murid not found")
    return murid

@router.put("/{id}")
async def update_murid(id: int, data: MuridCreate):
    updated = await db.murid.update(where={"id": id}, data=data.dict())
    return {"message": "Murid updated", "data": updated}

@router.delete("/{id}")
async def delete_murid(id: int):
    await db.murid.delete(where={"id": id})
    return {"message": "Murid deleted"}
