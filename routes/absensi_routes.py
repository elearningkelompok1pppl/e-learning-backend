from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from main import db

router = APIRouter()

class AbsensiCreate(BaseModel):
    murid_id: int | None = None
    kelas_id: int | None = None
    mata_pelajaran_id: int | None = None
    tanggal: datetime
    status: str
    keterangan: str | None = None
    guru_id: int | None = None


@router.post("/")
async def create_absensi(absensi: AbsensiCreate):
    try:
        created = await db.absensi.create(data=absensi.dict())
        return {"message": "Absensi created successfully", "data": created}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/")
async def get_all_absensi():
    return await db.absensi.find_many(include={"murid": True, "kelas": True, "mata_pelajaran": True, "guru": True})


@router.get("/{id}")
async def get_absensi(id: int):
    absensi = await db.absensi.find_unique(where={"id": id}, include={"murid": True, "kelas": True})
    if not absensi:
        raise HTTPException(404, "Absensi not found")
    return absensi


@router.put("/{id}")
async def update_absensi(id: int, data: AbsensiCreate):
    existing = await db.absensi.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "Absensi not found")
    updated = await db.absensi.update(where={"id": id}, data=data.dict())
    return {"message": "Absensi updated", "data": updated}


@router.delete("/{id}")
async def delete_absensi(id: int):
    existing = await db.absensi.find_unique(where={"id": id})
    if not existing:
        raise HTTPException(404, "Absensi not found")
    await db.absensi.delete(where={"id": id})
    return {"message": "Absensi deleted successfully"}
