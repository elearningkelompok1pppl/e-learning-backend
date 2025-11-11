from fastapi import APIRouter, HTTPException
from generated.prisma import Prisma
from pydantic import BaseModel
from main import db

router = APIRouter()

class GuruCreate(BaseModel):
    nama: str
    email: str
    password: str
    nip: str | None = None
    mata_pelajaran_text: str | None = None
    foto_profil: str | None = None
    no_telepon: str | None = None
    alamat: str | None = None
    status: str = "Aktif"

@router.post("/")
async def create_guru(guru: GuruCreate):
    created = await db.guru.create(data=guru.dict())
    return {"message": "Guru created successfully", "data": created}

@router.get("/")
async def get_all_guru():
    return await db.guru.find_many()

@router.get("/{id}")
async def get_guru(id: int):
    guru = await db.guru.find_unique(where={"id": id})
    if not guru:
        raise HTTPException(404, "Guru not found")
    return guru

@router.put("/{id}")
async def update_guru(id: int, data: GuruCreate):
    updated = await db.guru.update(where={"id": id}, data=data.dict())
    return {"message": "Guru updated", "data": updated}

@router.delete("/{id}")
async def delete_guru(id: int):
    await db.guru.delete(where={"id": id})
    return {"message": "Guru deleted"}
