from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from main import db

router = APIRouter()

class MateriCreate(BaseModel):
    judul: str
    konten: str
    file_materi: str | None = None
    tipe_file: str | None = None
    mata_pelajaran_id: int | None = None
    guru_id: int | None = None
    kelas_id: int | None = None

@router.post("/")
async def create_materi(data: MateriCreate):
    return await db.materi.create(data=data.dict())

@router.get("/")
async def get_all_materi():
    return await db.materi.find_many()

@router.get("/{id}")
async def get_materi(id: int):
    materi = await db.materi.find_unique(where={"id": id})
    if not materi:
        raise HTTPException(404, "Materi not found")
    return materi

@router.put("/{id}")
async def update_materi(id: int, data: MateriCreate):
    return await db.materi.update(where={"id": id}, data=data.dict())

@router.delete("/{id}")
async def delete_materi(id: int):
    await db.materi.delete(where={"id": id})
    return {"message": "Materi deleted"}
