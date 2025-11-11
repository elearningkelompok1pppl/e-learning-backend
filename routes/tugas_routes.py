from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from main import db

router = APIRouter()

class TugasCreate(BaseModel):
    judul: str
    deskripsi: str | None = None
    mata_pelajaran_id: int | None = None
    kelas_id: int | None = None
    guru_id: int | None = None
    deadline: datetime | None = None
    bobot: int | None = 100
    file_tugas: str | None = None
    status: str = "Active"


@router.post("/")
async def create_tugas(tugas: TugasCreate):
    try:
        created = await db.tugas.create(data=tugas.dict())
        return {"message": "Tugas created successfully", "data": created}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/")
async def get_all_tugas():
    return await db.tugas.find_many(include={"guru": True, "kelas": True, "mata_pelajaran": True})


@router.get("/{id}")
async def get_tugas(id: int):
    tugas = await db.tugas.find_unique(where={"id": id}, include={"guru": True, "kelas": True})
    if not tugas:
        raise HTTPException(404, "Tugas not found")
    return tugas


@router.put("/{id}")
async def update_tugas(id: int, data: TugasCreate):
    existing = await db.tugas.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "Tugas not found")
    updated = await db.tugas.update(where={"id": id}, data=data.dict())
    return {"message": "Tugas updated", "data": updated}


@router.delete("/{id}")
async def delete_tugas(id: int):
    existing = await db.tugas.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "Tugas not found")
    await db.tugas.delete(where={"id": id})
    return {"message": "Tugas deleted successfully"}
