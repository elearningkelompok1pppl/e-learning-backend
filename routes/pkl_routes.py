from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from main import db

router = APIRouter()

class PKLCreate(BaseModel):
    murid_id: int | None = None
    partner_id: int | None = None
    jurusan_id: int | None = None
    tanggal_mulai: datetime | None = None
    tanggal_selesai: datetime | None = None
    pembimbing_sekolah_id: int | None = None
    pembimbing_industri: str | None = None
    nilai: float | None = None
    keterangan: str | None = None
    status: str = "Sedang Berjalan"


@router.post("/")
async def create_pkl(pkl: PKLCreate):
    try:
        created = await db.pkl.create(data=pkl.dict())
        return {"message": "PKL created successfully", "data": created}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/")
async def get_all_pkl():
    return await db.pkl.find_many(include={"murid": True, "partner": True, "jurusan": True, "pembimbing_sekolah": True})


@router.get("/{id}")
async def get_pkl(id: int):
    pkl = await db.pkl.find_unique(where={"id": id}, include={"murid": True, "partner": True})
    if not pkl:
        raise HTTPException(404, "PKL not found")
    return pkl


@router.put("/{id}")
async def update_pkl(id: int, data: PKLCreate):
    existing = await db.pkl.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "PKL not found")
    updated = await db.pkl.update(where={"id": id}, data=data.dict())
    return {"message": "PKL updated", "data": updated}


@router.delete("/{id}")
async def delete_pkl(id: int):
    existing = await db.pkl.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "PKL not found")
    await db.pkl.delete(where={"id": id})
    return {"message": "PKL deleted successfully"}
