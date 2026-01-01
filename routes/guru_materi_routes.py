from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from main import db
from core.permissions import authorize_access

router = APIRouter(
    tags=["Guru - Materi"],
    dependencies=[Depends(authorize_access)]
)

class MateriCreate(BaseModel):
    judul: str
    konten: str
    file_materi: str | None = None
    tipe_file: str | None = None
    mata_pelajaran_id: int
    kelas_id: int


# ===============================
# CREATE MATERI (GURU)
# ===============================
@router.post("")
async def create_materi(data: MateriCreate, user=Depends(authorize_access)):
    if user["role"] != "Guru":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    guru = await db.guru.find_unique(where={"email": user["sub"]})
    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    materi = await db.materi.create(
        data={
            "judul": data.judul,
            "konten": data.konten,
            "file_materi": data.file_materi,
            "tipe_file": data.tipe_file,
            "mata_pelajaran_id": data.mata_pelajaran_id,
            "kelas_id": data.kelas_id,
            "guru_id": guru.id
        }
    )

    return {
        "message": "Materi berhasil dibuat",
        "data": materi
    }


# ===============================
# GET MATERI BY MAPEL
# ===============================
@router.get("")
async def get_materi_by_mapel(
    mata_pelajaran_id: int = Query(..., description="ID Mata Pelajaran"),
    user=Depends(authorize_access)
):
    # Guru & Murid boleh lihat materi
    if user["role"] not in ["Guru", "Murid"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")

    materi = await db.materi.find_many(
        where={
            "mata_pelajaran_id": mata_pelajaran_id
        },
        include={
            "guru": True,
            "kelas": True,
            "mata_pelajaran": True
        },
        order={"created_at": "desc"}
    )

    return {
        "total": len(materi),
        "data": materi
    }
