from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from main import db
from core.permissions import authorize_access
from datetime import datetime

router = APIRouter(
    tags=["Murid - Quiz"],
    dependencies=[Depends(authorize_access)]
)

@router.get("")
async def get_quiz_murid(user=Depends(authorize_access)):
    if user["role"] != "Murid":
        raise HTTPException(403, "Akses ditolak")

    murid = await db.murid.find_unique(where={"email": user["sub"]})

    quiz = await db.quiz.find_many(
        where={
            "kelas_id": murid.kelas_id,
            "status": "Published"
        },
        include={"mata_pelajaran": True}
    )

    return {"total": len(quiz), "data": quiz}

@router.get("/{quiz_id}/soal")
async def get_soal_quiz(quiz_id: int, user=Depends(authorize_access)):
    soal = await db.soal_quiz.find_many(
        where={"quiz_id": quiz_id},
        select={
            "id": True,
            "pertanyaan": True,
            "pilihan_a": True,
            "pilihan_b": True,
            "pilihan_c": True,
            "pilihan_d": True,
        }
    )
    return soal

class SubmitQuiz(BaseModel):
    quiz_id: int
    jawaban: dict  # { soal_id: "A"/"B"/"C"/"D" }

@router.post("/submit")
async def submit_quiz(data: SubmitQuiz, user=Depends(authorize_access)):
    murid = await db.murid.find_unique(where={"email": user["sub"]})

    soal_list = await db.soal_quiz.find_many(where={"quiz_id": data.quiz_id})

    benar = 0
    for soal in soal_list:
        if data.jawaban.get(str(soal.id)) == soal.jawaban_benar:
            benar += soal.bobot or 1

    hasil = await db.hasil_quiz.create(
        data={
            "murid_id": murid.id,
            "quiz_id": data.quiz_id,
            "score": benar,
            "jawaban_benar": benar,
            "total_soal": len(soal_list)
        }
    )

    return {
        "message": "Quiz selesai",
        "score": benar,
        "total_soal": len(soal_list)
    }
