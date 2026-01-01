from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from main import db
from core.permissions import authorize_access
from datetime import datetime

router = APIRouter(
    tags=["Guru - Quiz"],
    dependencies=[Depends(authorize_access)]
)

class QuizCreate(BaseModel):
    judul: str
    deskripsi: str | None = None
    mata_pelajaran_id: int
    kelas_id: int
    durasi: int

class SoalCreate(BaseModel):
    quiz_id: int
    pertanyaan: str
    pilihan_a: str
    pilihan_b: str
    pilihan_c: str
    pilihan_d: str
    jawaban_benar: str
    bobot: int = 1

@router.post("")
async def create_quiz(data: QuizCreate, user=Depends(authorize_access)):
    if user["role"] != "Guru":
        raise HTTPException(403, "Akses ditolak")

    guru = await db.guru.find_unique(where={"email": user["sub"]})

    quiz = await db.quiz.create(
        data={
            "judul": data.judul,
            "deskripsi": data.deskripsi,
            "mata_pelajaran_id": data.mata_pelajaran_id,
            "kelas_id": data.kelas_id,
            "guru_id": guru.id,
            "durasi": data.durasi,
            "status": "Draft"
        }
    )

    return {"message": "Quiz berhasil dibuat", "data": quiz}

@router.post("/soal")
async def add_soal(data: SoalCreate, user=Depends(authorize_access)):
    if user["role"] != "Guru":
        raise HTTPException(403, "Akses ditolak")

    soal = await db.soal_quiz.create(data=data.dict())
    return {"message": "Soal berhasil ditambahkan", "data": soal}

@router.get("")
async def get_quiz_by_mapel(
    mata_pelajaran_id: int,
    user=Depends(authorize_access)
):
    if user["role"] != "Guru":
        raise HTTPException(403, "Akses ditolak")

    guru = await db.guru.find_unique(where={"email": user["sub"]})

    quiz = await db.quiz.find_many(
        where={
            "mata_pelajaran_id": mata_pelajaran_id,
            "guru_id": guru.id
        },
        order={"created_at": "desc"}
    )

    return quiz

@router.get("/{quiz_id}/soal")
async def get_soal_by_quiz_guru(
    quiz_id: int,
    user=Depends(authorize_access)
):
    if user["role"] != "Guru":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    guru = await db.guru.find_unique(
        where={"email": user["sub"]}
    )

    if not guru:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    # Pastikan quiz ini milik guru tsb
    quiz = await db.quiz.find_first(
        where={
            "id": quiz_id,
            "guru_id": guru.id
        }
    )

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz tidak ditemukan")

    soal = await db.soal_quiz.find_many(
        where={"quiz_id": quiz_id},
        order={"id": "asc"} 
    )


    total_bobot = sum([s.bobot or 1 for s in soal])

    return {
        "quiz": {
            "id": quiz.id,
            "judul": quiz.judul,
            "durasi": quiz.durasi
        },
        "total_soal": len(soal),
        "total_poin": total_bobot,
        "data": soal
    }

@router.put("/{quiz_id}/publish")
async def publish_quiz(
    quiz_id: int,
    tanggal_mulai: datetime,
    tanggal_selesai: datetime,
    user=Depends(authorize_access)
):
    if user["role"] != "Guru":
        raise HTTPException(403, "Akses ditolak")

    guru = await db.guru.find_unique(where={"email": user["sub"]})

    quiz = await db.quiz.find_unique(where={"id": quiz_id})
    if not quiz or quiz.guru_id != guru.id:
        raise HTTPException(404, "Quiz tidak ditemukan")

    updated = await db.quiz.update(
        where={"id": quiz_id},
        data={
            "status": "Active",
            "tanggal_mulai": tanggal_mulai,
            "tanggal_selesai": tanggal_selesai
        }
    )

    return {
        "message": "Quiz berhasil dipublish",
        "data": updated
    }
