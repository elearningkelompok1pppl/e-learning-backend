from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from core.permissions import authorize_access
from main import db

router = APIRouter(
    tags=["Murid - Quiz"],
    dependencies=[Depends(authorize_access)]
)

# ===============================
# LIST QUIZ PER MAPEL
# ===============================
@router.get("/{mata_pelajaran_id}")
async def get_quiz_murid(
    mata_pelajaran_id: int,
    user=Depends(authorize_access)
):
    if user["role"] != "Murid":
        raise HTTPException(403, "Akses ditolak")

    murid = await db.murid.find_unique(where={"email": user["sub"]})
    if not murid or not murid.kelas_id:
        return {"total": 0, "data": []}

    quiz = await db.quiz.find_many(
        where={
            "mata_pelajaran_id": mata_pelajaran_id,
            "kelas_id": murid.kelas_id,
            "status": "Active"
        },
        include={"guru": True},
        order={"created_at": "desc"}
    )

    return {
        "total": len(quiz),
        "data": quiz
    }

# ===============================
# SOAL QUIZ
# ===============================
@router.get("/{quiz_id}/soal")
async def get_soal_quiz_murid(
    quiz_id: int,
    user=Depends(authorize_access)
):
    # ===============================
    # VALIDASI ROLE
    # ===============================
    if user["role"] != "Murid":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    # ===============================
    # AMBIL DATA MURID
    # ===============================
    murid = await db.murid.find_unique(
        where={"email": user["sub"]}
    )
    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")

    # ===============================
    # CEK APAKAH SUDAH PERNAH SUBMIT
    # ===============================
    hasil = await db.hasil_quiz.find_first(
        where={
            "quiz_id": quiz_id,
            "murid_id": murid.id
        }
    )

    if hasil:
        # 👉 SUDAH SUBMIT → KEMBALIKAN NILAI
        return {
            "status": "FINISHED",
            "message": "Quiz sudah dikerjakan",
            "nilai": {
                "score": hasil.score,
                "jawaban_benar": hasil.jawaban_benar,
                "total_soal": hasil.total_soal
            }
        }

    # ===============================
    # BELUM SUBMIT → AMBIL SOAL
    # ===============================
    soal = await db.soal_quiz.find_many(
        where={"quiz_id": quiz_id},
        order={"id": "asc"}
    )

    if not soal:
        raise HTTPException(status_code=404, detail="Soal tidak ditemukan")

    return {
        "status": "ONGOING",
        "total_soal": len(soal),
        "data": soal
    }


# ===============================
# SUBMIT QUIZ
# ===============================
class SubmitQuiz(BaseModel):
    jawaban: dict  # { soal_id: "A" }

@router.post("/{quiz_id}/submit")
async def submit_quiz_murid(
    quiz_id: int,
    data: SubmitQuiz,
    user=Depends(authorize_access)
):
    if user["role"] != "Murid":
        raise HTTPException(403, "Akses ditolak")

    murid = await db.murid.find_unique(
        where={"email": user["sub"]}
    )
    if not murid:
        raise HTTPException(404, "Murid tidak ditemukan")

    quiz = await db.quiz.find_unique(where={"id": quiz_id})
    if not quiz:
        raise HTTPException(404, "Quiz tidak ditemukan")

    soal_list = await db.soal_quiz.find_many(
        where={"quiz_id": quiz_id}
    )

    skor = 0
    benar = 0

    for soal in soal_list:
        bobot = soal.bobot or 1
        if data.jawaban.get(str(soal.id)) == soal.jawaban_benar:
            skor += bobot
            benar += 1

    await db.hasil_quiz.create(
        data={
            "murid_id": murid.id,
            "quiz_id": quiz_id,
            "mata_pelajaran_id": quiz.mata_pelajaran_id,
            "score": skor,
            "total_soal": len(soal_list),
            "jawaban_benar": benar,
            "waktu_selesai": datetime.utcnow()
        }
    )

    return {
        "message": "Quiz berhasil disubmit",
        "score": skor,
        "jawaban_benar": benar,
        "total_soal": len(soal_list)
    }
